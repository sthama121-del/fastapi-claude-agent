"""
FastAPI + Claude AI Agent
--------------------------
A simple but complete AI agent you can run locally and deploy to the cloud.

Endpoints:
  GET  /           → health check, confirms the server is alive
  GET  /info       → shows which Claude model is being used
  POST /chat       → send a message, get a Claude reply
  POST /chat/weather → same but Claude has a "weather tool" it can call
"""

import os
import json
import anthropic

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware

# ── Load your .env file so ANTHROPIC_API_KEY is available ─────────────────────
load_dotenv()

# ── Initialise the Anthropic client (reads ANTHROPIC_API_KEY automatically) ───
client = anthropic.Anthropic()

# ── The model we'll use throughout ────────────────────────────────────────────
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

# ── FastAPI app instance ───────────────────────────────────────────────────────
app = FastAPI(
    title="Claude AI Agent",
    description="A FastAPI wrapper around Claude — your personal AI agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)
# ==============================================================================
# REQUEST / RESPONSE SHAPES  (Pydantic keeps our data clean and validated)
# ==============================================================================

class ChatRequest(BaseModel):
    message: str                          # what the user types
    system_prompt: str | None = None      # optional override of personality

class ChatResponse(BaseModel):
    reply: str                            # Claude's answer
    model: str                            # which model answered
    input_tokens: int                     # how many tokens your message used
    output_tokens: int                    # how many tokens the reply used


# ==============================================================================
# TOOL DEFINITION  (this is what lets Claude "call a function")
# ==============================================================================

# We describe the tool in JSON so Claude knows it exists and when to use it.
WEATHER_TOOL = {
    "name": "get_weather",
    "description": (
        "Returns the current weather for a given city. "
        "Call this whenever the user asks about weather."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name, e.g. London, Tokyo, New York",
            }
        },
        "required": ["city"],
    },
}


def get_weather(city: str) -> str:
    """
    Fake weather function — swap this out for a real API (e.g. OpenWeatherMap)
    when you're ready to go further.
    """
    mock_data = {
        "london":        "12°C, overcast with light drizzle",
        "new york":      "18°C, partly cloudy",
        "tokyo":         "22°C, clear skies",
        "sydney":        "25°C, sunny",
        "san francisco": "16°C, foggy morning clearing by noon",
    }
    return mock_data.get(city.lower(), f"28°C, sunny and pleasant in {city}")


# ==============================================================================
# ROUTES
# ==============================================================================

@app.get("/")
def root():
    """Health check — if you hit this and get a 200, your server is alive."""
    return {"status": "ok", "message": "Claude AI Agent is running 🎉"}


@app.get("/info")
def info():
    """Returns basic info about the agent configuration."""
    return {
        "model": MODEL,
        "endpoints": ["/chat", "/chat/weather"],
        "note": "POST to /chat with {'message': 'hello'} to start",
    }


# ── Plain chat ─────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Send any message and get a Claude reply.
    Optionally override the system prompt to change Claude's personality.

    Example body:
        {"message": "Explain recursion in simple terms"}
    """
    system = request.system_prompt or "You are a helpful, friendly AI assistant."

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system,
            messages=[
                {"role": "user", "content": request.message}
            ],
        )
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid ANTHROPIC_API_KEY")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {str(e)}")

    return ChatResponse(
        reply=response.content[0].text,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


# ── Tool-calling chat (the "agent" behaviour) ─────────────────────────────────

@app.post("/chat/weather", response_model=ChatResponse)
def chat_with_weather_tool(request: ChatRequest):
    """
    Same as /chat but Claude can now *call the weather tool* when relevant.

    How it works:
      1. We send the user's message + the tool definition to Claude.
      2. If Claude decides to use the tool it returns a tool_use block.
      3. We run the real Python function and feed the result back.
      4. Claude then writes its final reply using that result.

    Example body:
        {"message": "What is the weather like in Tokyo right now?"}
    """
    system = request.system_prompt or (
        "You are a helpful assistant. When the user asks about weather, "
        "always use the get_weather tool to fetch the data."
    )

    messages = [{"role": "user", "content": request.message}]

    try:
        # ── Round 1: send to Claude with the tool available ────────────────
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system,
            tools=[WEATHER_TOOL],
            messages=messages,
        )

        # ── Did Claude decide to call a tool? ─────────────────────────────
        if response.stop_reason == "tool_use":
            tool_use_block = next(
                b for b in response.content if b.type == "tool_use"
            )
            city       = tool_use_block.input["city"]
            tool_result = get_weather(city)          # call our Python function

            # ── Round 2: give Claude the tool result so it can reply ───────
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": tool_result,
                }],
            })

            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system,
                tools=[WEATHER_TOOL],
                messages=messages,
            )

        # ── Extract the final text reply ───────────────────────────────────
        final_text = next(
            (b.text for b in response.content if hasattr(b, "text")),
            "I processed your request but had no text to return.",
        )

    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid ANTHROPIC_API_KEY")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {str(e)}")

    return ChatResponse(
        reply=final_text,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


# ==============================================================================
# ENTRY POINT  (used both locally and on cloud platforms like Render)
# ==============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀  Server starting on http://localhost:{port}")
    print(f"📖  Docs available at http://localhost:{port}/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
