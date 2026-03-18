# FastAPI Claude Agent — Production-Ready AI Agent API

> A production-grade REST API wrapping Anthropic Claude with tool-calling (agentic) capabilities, built on FastAPI with full OpenAPI documentation, Pydantic validation, and cloud deployment support.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-green)](https://fastapi.tiangolo.com/)
[![Claude](https://img.shields.io/badge/Anthropic-Claude%20Haiku-purple)](https://anthropic.com/)
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
  - API key authentication (x-api-key header)
  - Error handling (401, 502)
          |
          v
Anthropic Claude (configurable model, default: claude-haiku-4-5)
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

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | No | Health check |
| GET | `/info` | No | Agent configuration and available endpoints |
| POST | `/chat` | Yes | Single-turn conversation with Claude |
| POST | `/chat/weather` | Yes | Agentic chat — Claude calls weather tool when needed |

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI | REST endpoints with auto OpenAPI docs |
| LLM | Anthropic Claude (configurable) | Conversation and tool-calling |
| Validation | Pydantic v2 | Request/response schema enforcement |
| Server | Uvicorn | ASGI server for async performance |
| Tool Calling | Anthropic Tool Use API | Agentic function execution |
| Config | python-dotenv | Environment variable management |
| Auth | API key header middleware | Protect endpoints from unauthorized use |

---

## Getting Started

### Prerequisites
- Python 3.10+
- Anthropic API key from https://console.anthropic.com

### Installation

Clone the repository:
```
git clone https://github.com/sthama121-del/fastapi-claude-agent.git
cd fastapi-claude-agent
```

Create virtual environment:
```
python -m venv .venv
```

Activate on Windows:
```
.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:
```
source .venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the root directory:
```
ANTHROPIC_API_KEY=your-anthropic-key-here
APP_SECRET=your-chosen-secret-here
CLAUDE_MODEL=claude-haiku-4-5-20251001
```

- `ANTHROPIC_API_KEY` — your key from https://console.anthropic.com
- `APP_SECRET` — a password you choose; required in the `x-api-key` header for all POST requests
- `CLAUDE_MODEL` — optional; defaults to `claude-haiku-4-5-20251001` if not set

### Run the server
```
python main.py
```

API is live at http://localhost:8000
Interactive docs at http://localhost:8000/docs

---

## Authentication

The `/chat` and `/chat/weather` endpoints require an `x-api-key` header matching your `APP_SECRET`.

**Example with curl:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-chosen-secret-here" \
  -d '{"message": "What is RAG?"}'
```

**Example with PowerShell:**
```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/chat" `
  -ContentType "application/json" `
  -Headers @{"x-api-key"="your-chosen-secret-here"} `
  -Body '{"message": "What is RAG?"}'
```

Requests without the header return `401 Unauthorized`.

---

## Usage

### Plain conversation
```json
POST /chat
x-api-key: your-chosen-secret-here

{"message": "Explain the medallion architecture in data engineering"}
```

### Custom system prompt
```json
POST /chat
x-api-key: your-chosen-secret-here

{"message": "What is 2+2?", "system_prompt": "You are a data engineer. Answer everything with a data analogy."}
```

### Agentic tool-calling
```json
POST /chat/weather
x-api-key: your-chosen-secret-here

{"message": "What is the weather like in Tokyo?"}
```

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

---

## API Response Schema
```json
{
  "reply": "Claude's response text",
  "model": "claude-haiku-4-5-20251001",
  "input_tokens": 42,
  "output_tokens": 187
}
```

---

## Model Configuration

| Model | Speed | Cost | Use Case |
|-------|-------|------|----------|
| `claude-haiku-4-5-20251001` | Fastest | Cheapest | Default — demos, learning |
| `claude-sonnet-4-6` | Moderate | Moderate | Production workloads |
| `claude-opus-4-6` | Slower | Most expensive | Complex reasoning tasks |

Set in `.env`:
```
CLAUDE_MODEL=claude-sonnet-4-6
```

---

## Deployment

### Render (free tier)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `ANTHROPIC_API_KEY`, `APP_SECRET`, `CLAUDE_MODEL`

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Business Value

| Dimension | Impact |
|-----------|--------|
| Reusability | Any frontend or service can consume the API via REST |
| Observability | Token usage returned on every call for cost monitoring |
| Extensibility | New tools added as Python functions with JSON schema definitions |
| Reliability | Structured error handling for auth failures and API errors |
| Security | API key authentication protects endpoints from unauthorized use |
| Documentation | Auto-generated OpenAPI docs at /docs — zero extra effort |

---

## Future Enhancements

- Conversation memory — persist message history across turns using Redis
- Multiple tools — calculator, database query, web search tool support
- Streaming responses — real-time token streaming via Server-Sent Events
- Rate limiting — per-client request throttling
- Azure deployment — containerized deployment on Azure Container Apps

---

## Project Structure
```
fastapi-claude-agent/
  main.py            FastAPI application and all endpoints
  index.html         Frontend UI for browser-based testing
  requirements.txt   Python dependencies
  .gitignore         Git exclusions (includes .env)
  README.md          This file
```

---

## Author

Srikanth — Senior Data Engineer / AI Engineer
Specializing in agentic AI systems, API design, and GenAI pipelines.

GitHub: https://github.com/sthama121-del

---

## License

MIT License — free to use, modify, and distribute.