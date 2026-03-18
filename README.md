# FastAPI Claude Agent — Production-Ready AI Agent API

> A production-grade REST API wrapping Anthropic Claude with tool-calling (agentic) capabilities, built on FastAPI with full OpenAPI documentation, Pydantic validation, and cloud deployment support.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-green)](https://fastapi.tiangolo.com/)
[![Claude](https://img.shields.io/badge/Anthropic-Claude%20Sonnet-purple)](https://anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Problem Statement

Integrating LLMs into production systems requires more than calling an API — it requires proper request validation, error handling, tool orchestration, token tracking, and a clean interface for downstream consumers. This project demonstrates how to wrap a frontier LLM into a production-ready microservice that other systems can consume reliably.

---

## Architecture
```
Client (curl / Postman / frontend)
          |
          v
FastAPI REST API (main.py)
  - Pydantic request/response validation
  - CORS middleware
  - Error handling (401, 502)
          |
          v
Anthropic Claude (claude-sonnet)
  |
  |-- /chat          -> Single-turn LLM conversation
  |-- /chat/weather  -> Agentic tool-calling loop
          |
          v (tool-calling flow)
Tool Execution Layer
  - Claude decides when to call tools
  - Python function executes
  - Result fed back to Claude
  - Final response returned to client
```

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/info` | Agent configuration and available endpoints |
| POST | `/chat` | Single-turn conversation with Claude |
| POST | `/chat/weather` | Agentic chat — Claude calls weather tool when needed |

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI | REST endpoints with auto OpenAPI docs |
| LLM | Anthropic Claude Sonnet | Conversation and tool-calling |
| Validation | Pydantic v2 | Request/response schema enforcement |
| Server | Uvicorn | ASGI server for async performance |
| Tool Calling | Anthropic Tool Use API | Agentic function execution |
| Config | python-dotenv | Environment variable management |

---

## Getting Started

### Prerequisites
- Python 3.10+
- Anthropic API key from https://console.anthropic.com

### Installation

Clone the repository:
  git clone https://github.com/sthama121-del/fastapi-claude-agent.git
  cd fastapi-claude-agent

Create virtual environment:
  python -m venv .venv

Activate on Windows:
  .venv\Scripts\Activate.ps1

Activate on macOS/Linux:
  source .venv/bin/activate

Install dependencies:
  pip install -r requirements.txt

Configure API key:
  Create a .env file in the root directory:
  ANTHROPIC_API_KEY=your-key-here

Run the server:
  python main.py

API is live at http://localhost:8000
Interactive docs at http://localhost:8000/docs

---

## Usage

### Plain conversation

  POST /chat
  {"message": "Explain the medallion architecture in data engineering"}

### Custom system prompt

  POST /chat
  {"message": "What is 2+2?", "system_prompt": "You are a data engineer. Answer everything with a data analogy."}

### Agentic tool-calling

  POST /chat/weather
  {"message": "What is the weather like in Tokyo?"}

The agent automatically decides when to invoke the weather tool, executes it, and incorporates the result into its response — no manual orchestration required.

---

## How Tool Calling Works
```
User: "What is the weather in Tokyo?"
        |
        v
Round 1: Claude receives message + tool definition
        |
        v
Claude decides: call get_weather(city="Tokyo")
        |
        v
Python function executes -> returns weather data
        |
        v
Round 2: Claude receives tool result
        |
        v
Claude generates final natural language response
```

This is the core pattern behind production AI agents — the LLM reasons about when to use tools, your code executes them, and the LLM synthesizes the results.

---

## API Response Schema

Every /chat and /chat/weather response returns:

  {
    "reply": "Claude's response text",
    "model": "claude-sonnet-4-20250514",
    "input_tokens": 42,
    "output_tokens": 187
  }

Token counts are returned on every call for cost tracking and observability.

---

## Deployment

The app is cloud-ready. Deploy to any platform that supports Python:

### Render (free tier)
Build command: pip install -r requirements.txt
Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Environment variable: ANTHROPIC_API_KEY

### Docker
  FROM python:3.11-slim
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

---

## Business Value

| Dimension | Impact |
|-----------|--------|
| Reusability | Any frontend or service can consume the API via REST |
| Observability | Token usage returned on every call for cost monitoring |
| Extensibility | New tools added as Python functions with JSON schema definitions |
| Reliability | Structured error handling for auth failures and API errors |
| Documentation | Auto-generated OpenAPI docs at /docs — zero extra effort |

---

## Future Enhancements

- Conversation memory — persist message history across turns using Redis
- Multiple tools — calculator, database query, web search tool support
- Streaming responses — real-time token streaming via Server-Sent Events
- Authentication — API key middleware for securing endpoints
- Rate limiting — per-client request throttling
- Azure deployment — containerized deployment on Azure Container Apps

---

## Project Structure

fastapi-claude-agent/
  main.py            FastAPI application and all endpoints
  index.html         Frontend UI for browser-based testing
  requirements.txt   Python dependencies
  .gitignore         Git exclusions
  README.md          This file

---

## Author

Srikanth — Senior Data Engineer / AI Engineer
Specializing in agentic AI systems, API design, and GenAI pipelines.

---

## License

MIT License — free to use, modify, and distribute.
