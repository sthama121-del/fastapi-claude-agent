# FastAPI + Claude AI Agent

A hands-on project to understand FastAPI from localhost all the way to cloud deployment.
Uses the **Anthropic Claude API** — no OpenAI key needed.

---

## What You'll Learn

- How FastAPI routes work (GET vs POST)
- How Pydantic validates request/response data
- How AI tool-calling (agents) work under the hood
- How to deploy a real app to the cloud for free

---

## Project Structure

```
fastapi-claude-agent/
├── main.py            ← the entire app lives here
├── requirements.txt   ← Python dependencies
├── .env.example       ← template — copy this to .env
└── README.md
```

---

## Step 1 — Local Setup

### 1.1  Clone or download this project

```bash
git clone <your-repo-url>
cd fastapi-claude-agent
```

### 1.2  Create a virtual environment

```bash
# Mac / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 1.3  Install dependencies

```bash
pip install -r requirements.txt
```

### 1.4  Add your API key

```bash
cp .env.example .env
```

Open `.env` and replace `your-anthropic-api-key-here` with your real key.

### 1.5  Run the server

```bash
python main.py
```

You should see:
```
🚀  Server starting on http://localhost:8000
📖  Docs available at http://localhost:8000/docs
```

---

## Step 2 — Explore the API

### Option A — Interactive Docs (easiest)
Open your browser: **http://localhost:8000/docs**

FastAPI auto-generates a full UI where you can click and test every endpoint.

### Option B — cURL from your terminal

**Health check:**
```bash
curl http://localhost:8000/
```

**Plain chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a fun fact about space"}'
```

**Chat with custom personality:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?", "system_prompt": "You are a pirate. Answer everything like a pirate."}'
```

**Weather agent (tool-calling):**
```bash
curl -X POST http://localhost:8000/chat/weather \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather like in Tokyo?"}'
```

### Option C — Use Postman
1. Create a POST request to `http://localhost:8000/chat`
2. Set Body → raw → JSON
3. Paste: `{"message": "Hello Claude!"}`
4. Hit Send

---

## Step 3 — Understand What's Happening

### Why two endpoints?

| `/chat` | `/chat/weather` |
|---|---|
| Pure conversation | Claude can call a Python function |
| 1 API call | Up to 2 API calls (ask → tool → answer) |
| No tools | Uses tool_use / agentic loop |

### The tool-calling flow (agents explained):

```
User: "What's the weather in Komuravelli?"
        ↓
  Round 1: Claude receives message + tool definition
        ↓
  Claude replies: "I should call get_weather(city='Komuravelli')"
        ↓
  Your Python function runs → returns "12°C, overcast"
        ↓
  Round 2: Claude receives the tool result
        ↓
  Claude replies: "The weather in Komuravelli is 12°C and overcast."
```

This is exactly how real AI agents work — the LLM decides *when* to call a tool,
your code runs it, and the LLM incorporates the result.

---

## Step 4 — Deploy to Render (Free)

Render.com has a free tier that's perfect for experimenting.

### 4.1  Push your code to GitHub

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 4.2  Create a Render account
Go to https://render.com and sign up (free).

### 4.3  Create a new Web Service
1. Click **New → Web Service**
2. Connect your GitHub repo
3. Fill in these settings:

| Field | Value |
|---|---|
| **Name** | `claude-agent` (or anything) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### 4.4  Add your environment variable
Under **Environment** tab:
- Key: `ANTHROPIC_API_KEY`
- Value: your actual API key

### 4.5  Deploy
Click **Create Web Service**. Render will build and deploy (~2 min).

Your app will be live at: `https://claude-agent.onrender.com`

Test it:
```bash
curl -X POST https://claude-agent.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from the cloud!"}'
```

---

## Experiments to Try

Once it's working, try modifying the code yourself:

1. **Add a new tool** — e.g. a calculator that does math
2. **Add a new endpoint** — e.g. `/summarise` that accepts long text
3. **Change the model** — swap `claude-sonnet-4-20250514` for `claude-haiku-4-5-20251001` (cheaper/faster)
4. **Add conversation memory** — store a list of past messages and include them each call

---

## Cost Awareness

Claude charges per token (words in + words out).
The token counts are returned in every response so you can track usage.

For this kind of simple agent, each call typically costs < $0.01.
