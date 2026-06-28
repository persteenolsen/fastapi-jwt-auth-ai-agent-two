# 🚀 FastAPI with JWT Auth serving a Tool-Calling AI Agent

A production-style AI Agent API built with FastAPI, featuring JWT authentication and a structured tool-calling architecture powered by Groq LLMs.

This project implements a modern **3-phase Tool Agent Pipeline (Plan → Execute → Synthesize)** where tools are safely selected, executed, and used to generate grounded responses.

# Version

At Render I use the PYTHON_VERSION environment variable to ensure Python 3.11. Locally I am using Python 3.12.

---

## 📌 Project Info

- Version: 0.2.0
- Python: 3.11 / 3.12
- Architecture: Structured Tool Agent (Plan → Execute → Synthesize)
- Last Updated: 28-06-2026

---

## ✨ Key Features

### 🔐 Authentication
- JWT-based authentication (HS256)
- Protected /chat endpoint
- Token-based access control
- Environment-based credentials

---

### 🤖 AI Agent (Structured Tool System)

This system is a **tool-calling agent**, but with strict separation of responsibilities:

- Phase 1: Plan (LLM decides which tools to use)
- Phase 2: Execute (Python safely runs tools from registry)
- Phase 3: Synthesize (LLM generates final grounded response)

Key properties:
- LLM cannot directly execute tools
- Tools are validated through a registry
- Execution is deterministic and controlled
- Fallback to direct LLM response when no tools are needed

---

### 🧠 LLM Integration (Groq)
- Model: openai/gpt-oss-20b
- High-speed inference via Groq API
- Temperature set to 0 for deterministic behavior
- Used for:
  - Tool planning
  - Query rewriting (Wikidata)
  - Final synthesis

---

### 🧩 Tool Registry System
- Central TOOL_REGISTRY controls all available tools
- LLM receives tool capabilities dynamically
- Adding tools requires only registration, no architecture changes
- Built-in tools:
  - Wikipedia (general knowledge)
  - Wikidata (structured facts and rankings)
  - Calculator (safe arithmetic engine)

---

### ➗ Calculator Tool
- Safe AST-based arithmetic evaluator (no eval usage)
- Supports: +, -, *, /, %, **, // and parentheses
- Fully sandboxed execution
- Automatically used for valid math expressions

---

### 🌐 Wikipedia Tool
- Two-step retrieval:
  - Search API for entity resolution
  - Summary API for content extraction
- Robust retry handling and fallback logic

---

### 🧾 Wikidata Tool
- Structured entity and fact retrieval
- LLM-assisted query simplification
- Optimized for rankings and factual comparisons

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /login | Get JWT access token |
| POST | /chat | Chat with AI agent |
| GET | /health | Service health check |
| GET | /health/tools | All tools health check |
| GET | /health/tools/{tool_name} | Single tool health check |

---

## ⚙️ Getting Started

### 1. Clone Repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

---

### 2. Create Virtual Environment
python -m venv venv

Activate:
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

---

### 3. Install Dependencies
pip install -r requirements.txt

---

## 🔑 Environment Variables

Create a .env file:

SECRET_KEY=your_secret_key_here
GROQ_API_KEY=your_groq_api_key
FAKE_USERNAME=admin
FAKE_PASSWORD=password

Generate secret key:
python -c import secrets; print(secrets.token_hex(32))

---

## ▶️ Run Application

uvicorn main:app --reload

API: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

---

## 🔐 Authentication Flow

1. Call /login with credentials
2. Receive JWT token
3. Send token in header: Authorization: Bearer <token>
4. Access /chat endpoint

---

## 🧠 How the Agent Works

User message flows through a structured pipeline:

User Input
→ Phase 1: LLM plans tools (or none)
→ Phase 2: Python executes tools from registry
→ Phase 3: LLM synthesizes final grounded response

This ensures:
- deterministic execution
- safe tool usage
- reduced hallucination risk
- clear traceability of reasoning

---

## 🏗️ Architecture

### 🟢 Structured Tool Agent (Current System)

This system is built around a strict separation of concerns:

- Planner (LLM): decides which tools to use
- Executor (Python): runs tools safely
- Synthesizer (LLM): formats final answer

Key properties:
- No direct tool execution by LLM
- No ReAct loops or iterative reasoning
- One-pass planning per request
- Fully traceable execution steps

---

## 💬 Example Requests

### No Tool Example

POST /chat
{ "message": "Tell me a joke" }

Response:
Response: Why don’t skeletons fight each other? They don’t have the guts.
tools_used: []
steps: tool_plan=[]

---

### Calculator Example

POST /chat
{ "message": "What is 25 * 18 + 10?" }

Response:
Response: The calculation 25 × 18 + 10 equals 460.
tools_used: calculator tool executed successfully
steps: tool_plan includes calculator

---

### Wikipedia Example

POST /chat
{ "message": "What is AI?" }

Response:
Response: Artificial intelligence (AI) is the capability of computational systems to perform tasks associated with human intelligence...
tools_used: wikipedia tool executed successfully
steps: tool_plan includes wikipedia query

---

## 🚀 Benefits

- Clean separation of planning, execution, and reasoning
- Fully extensible tool system
- Safe and controlled tool execution
- Reduced hallucinations via tool grounding
- Easy to debug and trace decisions
- Production-ready FastAPI structure

---

## 🚧 Current Limitations

- Stateless per request
- Single planning step (no iterative refinement)
- No streaming responses yet
- Limited tool ecosystem

---

## 🚀 Future Improvements

- Conversation memory layer
- Streaming responses (WebSockets or SSE)
- Parallel tool execution
- Tool confidence scoring and reranking
- Caching for Wikipedia/Wikidata
- Multi-step planning (agent loops)

---

## 📄 License

MIT License

---

## 🙌 Final Notes

This project implements a modern structured tool-calling architecture where tools are first-class deterministic components and the LLM is used strictly for planning and synthesis. This creates a scalable and debuggable foundation for advanced AI agent systems.