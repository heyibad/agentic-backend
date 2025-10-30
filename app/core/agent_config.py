import json
import os
from uuid import uuid4
from typing import cast
import app
from app.core.config import settings

from dotenv import load_dotenv

from pydantic import BaseModel, Field
from datetime import datetime, UTC


# Import OpenAI Agents SDK components
from agents import (
    Agent,
    Runner,
    function_tool,
    OpenAIChatCompletionsModel,
    RunConfig,
    ModelProvider,
)
from openai import AsyncOpenAI

# Load the environment variables from the .env file
load_dotenv()


external_client = AsyncOpenAI(
    api_key=settings.api_key,
    base_url=settings.api_base_url,
)

model = OpenAIChatCompletionsModel(model=settings.model, openai_client=external_client)

config = RunConfig(
    model=model,
    model_provider=cast(ModelProvider, external_client),  # satisfy type checker
    tracing_disabled=True,
)


# Example Tool: Create a tool to fetch the current time
@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


# Create an AI agent using OpenAI Agents SDK
chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot.",
    tools=[get_current_time],  # Add the time tool
    model=model,
)
