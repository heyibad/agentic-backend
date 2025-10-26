from __future__ import annotations

import json
from typing import AsyncIterator, Any
from uuid import UUID

from agents import Runner
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from openai.types.responses import ResponseTextDeltaEvent
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.agent_config import chat_agent, config
from app.core.security import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schema.chat import (
    ChatCompletionResponse,
    ChatMessageResponse,
    ChatPrompt,
    ChatStreamDelta,
    ConversationResponse,
    MessageRole,
    MessageStatus,
)
from app.utils.db import get_db


router = APIRouter(prefix="/chat", tags=["Chat"])


async def _resolve_conversation(
    prompt: ChatPrompt, db: AsyncSession, current_user: User
) -> Conversation:
    if prompt.conversation_id:
        conversation = await db.get(Conversation, prompt.conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        return conversation

    conversation = Conversation(
        user_id=current_user.id,
        title=prompt.text[:80] if prompt.text else None,
    )
    db.add(conversation)
    await db.flush()
    return conversation


def _build_message_metadata(prompt: ChatPrompt) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    if prompt.metadata:
        meta["client_metadata"] = prompt.metadata.model_dump(mode="json")
    if prompt.tags:
        meta["tags"] = prompt.tags
    return meta


@router.post("", response_model=ChatCompletionResponse)
async def chat(
    prompt: ChatPrompt,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not prompt.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message text cannot be empty",
        )

    conversation = await _resolve_conversation(prompt, db, current_user)

    user_message = Message(
        conversation_id=conversation.id,
        author_id=prompt.author_id or current_user.id,
        role=MessageRole.USER.value,
        content=prompt.text,
        status=MessageStatus.COMPLETED.value,
        provider_meta=_build_message_metadata(prompt) or None,
    )

    db.add(user_message)
    await db.flush()

    result = await Runner.run(chat_agent, input=prompt.text, run_config=config)
    reply_text = (result.final_output or "").strip()

    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT.value,
        content=reply_text,
        status=MessageStatus.COMPLETED.value,
        tokens=len(reply_text.split()),
    )

    db.add(assistant_message)
    await db.commit()

    await db.refresh(conversation)
    await db.refresh(user_message)
    await db.refresh(assistant_message)

    return ChatCompletionResponse(
        conversation=ConversationResponse.model_validate(conversation),
        request_message=ChatMessageResponse.model_validate(user_message),
        response_message=ChatMessageResponse.model_validate(assistant_message),
    )


async def _stream_agent_response(
    prompt: ChatPrompt,
    conversation_id: UUID,
    user_message_id: UUID,
    assistant_message_id: UUID,
    db: AsyncSession,
) -> AsyncIterator[str]:
    """
    Stream AI agent response in real-time via SSE.

    Args:
        prompt: User input prompt
        conversation_id: ID of the conversation (extracted before stream)
        user_message_id: ID of user message (extracted before stream)
        assistant_message_id: ID of assistant message (extracted before stream)
        db: Database session
    """
    buffer: list[str] = []

    # Fetch full objects for initial snapshot
    conversation = await db.get(Conversation, conversation_id)
    user_message = await db.get(Message, user_message_id)
    assistant_message = await db.get(Message, assistant_message_id)

    if not conversation or not user_message or not assistant_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation or messages",
        )

    # Send initial snapshot with full conversation and message data
    snapshot = {
        "conversation": {
            "id": str(conversation.id),
            "title": conversation.title,
            "model": conversation.model,
            "user_id": str(conversation.user_id),
            "created_at": conversation.created_at.isoformat(),
        },
        "request_message": {
            "id": str(user_message.id),
            "conversation_id": str(user_message.conversation_id),
            "role": user_message.role,
            "content": user_message.content,
            "status": user_message.status,
            "created_at": user_message.created_at.isoformat(),
        },
        "response_message": {
            "id": str(assistant_message.id),
            "conversation_id": str(assistant_message.conversation_id),
            "role": assistant_message.role,
            "content": assistant_message.content,
            "status": "streaming",
            "created_at": assistant_message.created_at.isoformat(),
        },
    }
    yield f"event: snapshot\ndata: {json.dumps(snapshot)}\n\n"

    try:
        stream = Runner.run_streamed(chat_agent, input=prompt.text, run_config=config)
        async for event in stream.stream_events():
            if event.type != "raw_response_event" or not isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                continue
            delta = event.data.delta or ""
            if not delta:
                continue
            buffer.append(delta)
            chunk = ChatStreamDelta(
                conversation_id=conversation_id,
                message_id=assistant_message_id,
                delta=delta,
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
    except Exception as e:
        # Update message status to failed
        assistant_msg = await db.get(Message, assistant_message_id)
        if assistant_msg:
            assistant_msg.status = MessageStatus.FAILED.value
            assistant_msg.content = "".join(buffer)
            await db.commit()

        done_chunk = ChatStreamDelta(
            conversation_id=conversation_id,
            message_id=assistant_message_id,
            delta="",
            done=True,
        )
        yield f"data: {done_chunk.model_dump_json()}\n\n"
        raise

    # Update assistant message with final content
    assistant_msg = await db.get(Message, assistant_message_id)
    if assistant_msg:
        assistant_msg.content = "".join(buffer)
        assistant_msg.status = MessageStatus.COMPLETED.value
        assistant_msg.tokens = len(assistant_msg.content.split())
        await db.commit()

    done_chunk = ChatStreamDelta(
        conversation_id=conversation_id,
        message_id=assistant_message_id,
        delta="",
        done=True,
    )
    yield f"data: {done_chunk.model_dump_json()}\n\n"


@router.post("/stream")
async def chat_stream(
    prompt: ChatPrompt,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not prompt.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message text cannot be empty",
        )

    conversation = await _resolve_conversation(prompt, db, current_user)

    user_message = Message(
        conversation_id=conversation.id,
        author_id=prompt.author_id or current_user.id,
        role=MessageRole.USER.value,
        content=prompt.text,
        status=MessageStatus.COMPLETED.value,
        provider_meta=_build_message_metadata(prompt) or None,
    )

    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT.value,
        content="",
        status=MessageStatus.PENDING.value,
    )

    db.add(user_message)
    db.add(assistant_message)
    await db.flush()

    # Extract IDs before commit to avoid lazy loading during streaming
    conversation_id = conversation.id
    user_message_id = user_message.id
    assistant_message_id = assistant_message.id

    await db.commit()

    return StreamingResponse(
        _stream_agent_response(
            prompt, conversation_id, user_message_id, assistant_message_id, db
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
