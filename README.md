# 🚀 FastAPI Tool-Calling AI Agent (JWT + Structured LLM Pipeline)

A production-style AI Agent API built with FastAPI, featuring JWT authentication and a structured tool-calling architecture powered by Groq LLMs.

The agent follows a deterministic **Plan → Execute → Synthesize** pipeline, where the LLM proposes tool usage while Python retains full control over execution. This separation keeps tool usage safe, predictable, and easy to extend.

---

# Version

Production (Render) uses the `PYTHON_VERSION` environment variable with **Python 3.11**. Local development uses **Python 3.12**.

---

## 📌 Project Info

- Version: 0.2.1
- Python: 3.11 / 3.12
- Architecture: Plan → Execute → Synthesize
- Last Updated: 01-07-2026

---

## 🎯 Use Cases

This project can serve as the foundation for:

- 🤖 AI assistants
- ⚡ FastAPI AI backends
- 🧠 Tool-augmented LLM systems
- 🧪 Agent experimentation
- 🎓 Educational projects
- 🔬 LLM tool-calling research
- 🔌 Plugin- and API-driven AI applications
- 🏢 Internal enterprise AI services

---

## ✨ Key Features

### 🔐 Authentication

- JWT authentication (HS256)
- Protected `/chat` endpoint
- Token-based authorization
- Environment-based configuration

---

### 🤖 Structured AI Agent

The agent follows a simple three-phase pipeline:

1. **Plan** – The LLM decides whether tools are needed.
2. **Execute** – Python validates and safely executes approved tools.
3. **Synthesize** – The LLM generates a grounded final response using tool results.

Key properties:

- LLM never executes tools directly
- Tool access is controlled through a registry
- Deterministic execution in Python
- Safe fallback when no tools are required

---

### 🧠 LLM Integration (Groq)

- Primary model: `openai/gpt-oss-120b`
- Stable model: `openai/gpt-oss-20b`
- High-speed inference through Groq
- Temperature = 0 for deterministic planning

Used for:

- Tool planning
- Wikidata query simplification
- Final response synthesis

---

### 🛡️ Robust JSON Safety Layer

Since LLMs may occasionally return malformed structured output, the agent includes a defensive parsing layer that:

- Safely extracts JSON from mixed responses
- Validates tool schemas
- Rejects malformed tool definitions
- Logs parsing errors
- Falls back safely without crashing

---

### 🧩 Tool Registry

A centralized `TOOL_REGISTRY` defines every available tool.

Benefits:

- Controlled tool access
- Easy extensibility
- No architectural changes when adding tools

Current tools:

- Wikipedia
- Wikidata
- Calculator

---

### ➗ Calculator

- Safe AST-based arithmetic (no `eval`)
- Supports `+ - * / % ** //` and parentheses
- Sandboxed execution

---

### 🌐 Wikipedia

- Search API for entity resolution
- Summary API for content retrieval
- Retry and fallback handling

---

### 🧾 Wikidata

- Structured fact retrieval
- LLM-assisted query rewriting
- Optimized for rankings and comparisons

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Get JWT token |
| POST | `/chat` | Chat with the AI agent |
| GET | `/health` | Service health |
| GET | `/health/tools/{tool_name}` | Tool health |

---

## ⚙️ Getting Started

### Clone

git clone https://github.com/your-username/your-repo.git

cd your-repo

### Create Virtual Environment

python -m venv venv

Windows:

venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

### Install

pip install -r requirements.txt

---

## 🔑 Environment Variables

Create a `.env` file:

SECRET_KEY=your_secret_key_here

GROQ_API_KEY=your_groq_api_key

FAKE_USERNAME=admin

FAKE_PASSWORD=password

Generate a secret key:

python -c "import secrets; print(secrets.token_hex(32))"

---

## ▶️ Run

uvicorn main:app --reload

API:

http://127.0.0.1:8000

Swagger Docs:

http://127.0.0.1:8000/docs

---

## 🔐 Authentication Flow

1. Request a JWT token from `/login`
2. Include it in the `Authorization: Bearer <token>` header
3. Access the protected `/chat` endpoint

---

## 🧠 How the Agent Works

User Input

→ Plan (LLM)

→ Execute (Python tools)

→ Synthesize (LLM)

This architecture provides:

- Safe tool execution
- Deterministic behavior
- Reduced hallucinations through tool grounding
- Full traceability

---

## 🏗️ Architecture

### 🔁 Model-Agnostic Design

The LLM is intentionally treated as a replaceable reasoning component.

It is responsible for:

- Tool planning
- Response synthesis

It is **not** responsible for:

- Tool execution
- Mathematical correctness
- External data retrieval
- Safety validation

These responsibilities remain entirely within deterministic Python code.

Changing models primarily affects reasoning quality—not system correctness or architecture.

---

## 🟢 Structured Tool Agent

Planner (LLM)

↓

Executor (Python)

↓

Synthesizer (LLM)

Core principles:

- LLM suggests actions
- Python enforces rules
- Tools perform deterministic work

---

## 💬 Example Requests

### No Tool

POST /chat

{ "message": "Tell me a joke" }

Response:

{
  "response": "Why don’t scientists trust atoms? Because they make up everything!",
  "tools_used": [],
  "steps": ["plan=[]"],
  "error_id": null
}

---

### Calculator

POST /chat

{ "message": "What is 25 * 18 + 10?" }

Response:

{
  "response": "460",
  "tools_used": [
    {
      "tool": "calculator",
      "query": "25 * 18 + 10",
      "success": true
    }
  ]
}

---

### Wikipedia

POST /chat

{ "message": "What is AI?" }

Response:

{
  "response": "Artificial intelligence is ...",
  "tools_used": [
    {
      "tool": "wikipedia",
      "query": "Artificial intelligence",
      "success": true
    }
  ]
}

---

### Wikidata

POST /chat

{ "message": "Where will the 2028 Summer Olympics take place?" }

Response:

{
  "response": "Los Angeles, United States",
  "tools_used": [
    {
      "tool": "wikidata",
      "query": "2028 Summer Olympics host city",
      "success": true
    }
  ]
}

---

## 🚀 Benefits

- Clean separation of concerns
- Extensible tool architecture
- Deterministic execution
- Grounded responses
- Easy debugging and traceability

---

## 🚧 Current Limitations

- Stateless requests
- Single planning step
- No streaming
- Limited tool ecosystem

---

## 🚀 Future Improvements

- Conversation memory
- Streaming (SSE/WebSockets)
- Parallel tool execution
- Tool confidence scoring
- Response caching
- Multi-step planning

---

## 💡 Design Philosophy

> **The LLM proposes what might make sense. Your code decides what is actually allowed.**

Separating **suggestion** from **enforcement** makes the system safer, easier to debug, and simpler to extend. The LLM explores possibilities, while Python validates requests, executes tools, and enforces system rules.

---

## 🙌 Final Notes

This project demonstrates a structured approach to AI agents where reasoning, execution, and safety are intentionally separated. The result is a modular architecture that can evolve with new tools or newer language models while keeping execution deterministic and controlled.

---

## 📄 License

MIT License