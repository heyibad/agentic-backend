# SSE Chat Streaming API Documentation

## Overview

The `/api/v1/chat/stream` endpoint provides real-time Server-Sent Events (SSE) streaming for AI chat responses, perfect for building responsive chat interfaces in Next.js.

## Endpoint

**POST** `/api/v1/chat/stream`

## Authentication

Requires Bearer token authentication:

```
Authorization: Bearer <your_access_token>
```

## Request Body

```json
{
    "text": "Your message here",
    "conversation_id": "uuid-optional", // Optional: continue existing conversation
    "author_id": "uuid-optional", // Optional: override author
    "metadata": {
        // Optional: client metadata
        "client": "nextjs-frontend",
        "session_id": "session-uuid",
        "tags": ["tag1", "tag2"],
        "extras": {}
    },
    "tags": [] // Optional: message tags
}
```

## Response Format

### Event Stream Structure

The endpoint returns a `text/event-stream` with the following events:

#### 1. Snapshot Event (First Event)

```
event: snapshot
data: {
  "conversation": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "...",
    "created_at": "2025-10-17T12:00:00Z"
  },
  "request_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "user message",
    "created_at": "2025-10-17T12:00:00Z"
  },
  "response_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "",
    "status": "pending",
    "created_at": "2025-10-17T12:00:00Z"
  }
}
```

#### 2. Delta Events (Streaming Chunks)

```
data: {
  "conversation_id": "uuid",
  "message_id": "uuid",
  "delta": "text chunk",
  "done": false
}
```

#### 3. Done Event (Final Event)

```
data: {
  "conversation_id": "uuid",
  "message_id": "uuid",
  "delta": "",
  "done": true
}
```

## Next.js Implementation Example

### Using Fetch API

```typescript
async function streamChat(message: string, token: string) {
    const response = await fetch("http://localhost:8080/api/v1/chat/stream", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text: message }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullText = "";

    while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
            if (line.startsWith("data: ")) {
                const jsonStr = line.substring(6);
                try {
                    const data = JSON.parse(jsonStr);

                    if (data.delta) {
                        fullText += data.delta;
                        // Update UI with fullText
                        console.log("Current text:", fullText);
                    }

                    if (data.done) {
                        console.log("Stream completed");
                        break;
                    }
                } catch (e) {
                    // Ignore parsing errors
                }
            }
        }
    }

    return fullText;
}
```

### React Hook Example

```typescript
import { useState, useCallback } from "react";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    isStreaming?: boolean;
}

export function useChatStream(token: string) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = useCallback(
        async (text: string) => {
            // Add user message
            const userMessage: Message = {
                id: Date.now().toString(),
                role: "user",
                content: text,
            };
            setMessages((prev) => [...prev, userMessage]);

            // Create assistant message placeholder
            const assistantId = (Date.now() + 1).toString();
            setMessages((prev) => [
                ...prev,
                {
                    id: assistantId,
                    role: "assistant",
                    content: "",
                    isStreaming: true,
                },
            ]);

            setIsLoading(true);

            try {
                const response = await fetch(
                    "http://localhost:8080/api/v1/chat/stream",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                        body: JSON.stringify({ text }),
                    }
                );

                const reader = response.body?.getReader();
                const decoder = new TextDecoder();
                let fullText = "";

                while (true) {
                    const { done, value } = await reader!.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split("\n");

                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            try {
                                const data = JSON.parse(line.substring(6));

                                if (data.delta) {
                                    fullText += data.delta;
                                    setMessages((prev) =>
                                        prev.map((msg) =>
                                            msg.id === assistantId
                                                ? { ...msg, content: fullText }
                                                : msg
                                        )
                                    );
                                }

                                if (data.done) {
                                    setMessages((prev) =>
                                        prev.map((msg) =>
                                            msg.id === assistantId
                                                ? { ...msg, isStreaming: false }
                                                : msg
                                        )
                                    );
                                }
                            } catch (e) {
                                // Ignore parse errors
                            }
                        }
                    }
                }
            } catch (error) {
                console.error("Stream error:", error);
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === assistantId
                            ? {
                                  ...msg,
                                  content: "Error: Failed to get response",
                                  isStreaming: false,
                              }
                            : msg
                    )
                );
            } finally {
                setIsLoading(false);
            }
        },
        [token]
    );

    return { messages, sendMessage, isLoading };
}
```

### Next.js Component Example

```typescript
"use client";

import { useChatStream } from "@/hooks/useChatStream";
import { useState } from "react";

export default function ChatInterface({ token }: { token: string }) {
    const [input, setInput] = useState("");
    const { messages, sendMessage, isLoading } = useChatStream(token);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        await sendMessage(input);
        setInput("");
    };

    return (
        <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
            <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`p-4 rounded-lg ${
                            msg.role === "user"
                                ? "bg-blue-100 ml-auto max-w-[80%]"
                                : "bg-gray-100 mr-auto max-w-[80%]"
                        }`}
                    >
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        {msg.isStreaming && (
                            <span className="text-sm text-gray-500 animate-pulse">
                                ●
                            </span>
                        )}
                    </div>
                ))}
            </div>

            <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 p-2 border rounded"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
                >
                    Send
                </button>
            </form>
        </div>
    );
}
```

## Error Handling

### Common Errors

-   **400 Bad Request**: Empty message text
-   **401 Unauthorized**: Invalid or missing token
-   **404 Not Found**: Invalid conversation_id
-   **500 Internal Server Error**: Server error during streaming

### Error Response Format

Standard HTTP error responses (not SSE format):

```json
{
    "detail": "Error message"
}
```

## Best Practices

1. **Connection Management**

    - Always close the reader when done or on error
    - Implement proper cleanup in useEffect hooks

2. **UI Updates**

    - Update UI incrementally as deltas arrive
    - Show loading/streaming indicator
    - Handle connection interruptions gracefully

3. **Performance**

    - Use React.memo for message components
    - Virtualize long message lists
    - Debounce rapid updates if needed

4. **CORS**
    - Ensure backend CORS settings allow your frontend origin
    - Current backend allows: `http://localhost:3000,http://localhost:8080`

## Testing

### Test HTML File

A test HTML file is provided at `test_sse_stream.html` for manual testing:

```bash
# Open in browser
start test_sse_stream.html  # Windows
open test_sse_stream.html   # macOS
```

### cURL Test

```bash
curl -N -X POST http://localhost:8080/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"text":"Hello, how are you?"}'
```

## Troubleshooting

### Stream Not Appearing in Real-Time

-   Check browser network tab for buffering
-   Verify `Cache-Control: no-cache` header is set
-   Ensure nginx/proxy doesn't buffer SSE responses

### Connection Drops

-   Implement reconnection logic in frontend
-   Add ping/keepalive messages if needed
-   Check backend timeout settings

### Messages Not Updating

-   Verify state updates in React components
-   Check console for parsing errors
-   Ensure delta text is being accumulated correctly

## Server Configuration

The backend is configured with optimal SSE headers:

```python
headers={
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # Disables nginx buffering
}
```

## Support

For issues or questions, contact the backend team or check the API logs.
