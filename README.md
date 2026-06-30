# 🚀 FastAPI Tool-Calling AI Agent (JWT + Structured LLM Pipeline)

A production-style AI Agent API built with FastAPI, featuring JWT authentication and a structured tool-calling architecture powered by Groq LLMs.

This project implements a modern **3-phase Tool Agent Pipeline (Plan → Execute → Synthesize)** where tools are safely selected, executed, and used to generate grounded responses.

---

# Version

At Render I use the `PYTHON_VERSION` environment variable to ensure Python 3.11. Locally I am using Python 3.12.

---

## 📌 Project Info

- Version: 0.2.1
- Python: 3.11 / 3.12
- Architecture: Structured Tool Agent (Plan → Execute → Synthesize)
- Last Updated: 30-06-2026

---

## ✨ Key Features

### 🔐 Authentication
- JWT-based authentication (HS256)
- Protected `/chat` endpoint
- Token-based access control
- Environment-based credentials

---

### 🤖 AI Agent (Structured Tool System)

This system implements a deterministic tool-calling architecture:

- Phase 1: Plan (LLM selects tools or no tools)
- Phase 2: Execute (Python safely runs tools from registry)
- Phase 3: Synthesize (LLM generates final grounded response)

Key properties:
- LLM cannot directly execute tools
- Tools are validated through a strict registry
- Execution is deterministic and fully controlled
- Safe fallback to direct LLM response when no tools are needed

---

### 🧠 LLM Integration (Groq)

- Model: `openai/gpt-oss-120b` (primary, under evaluation)
- Model: `openai/gpt-oss-20b` (tested and stable)
- High-speed inference via Groq API
- Temperature set to 0 for deterministic behavior
- Used for:
  - Tool planning
  - Wikidata query rewriting
  - Final synthesis

---

### 🛡️ Robust JSON Safety Layer (NEW)

The system now includes an improved **robust JSON parsing layer** for LLM outputs.

Because LLMs may return malformed or noisy structured outputs, the system ensures stability by:

- Extracting JSON safely from mixed text responses
- Strict schema validation (`dict → tools list → tool objects`)
- Rejecting malformed tool definitions
- Logging parsing issues for debugging
- Never crashing the agent on invalid model output
- Always failing safely with an empty tool list

This makes the agent resilient to:
- Extra explanatory text around JSON
- Broken or partial JSON responses
- Missing or malformed tool definitions

---

### 🧩 Tool Registry System

- Central `TOOL_REGISTRY` controls all available tools
- LLM receives tool capabilities dynamically
- Adding tools requires no architectural changes
- Built-in tools:
  - Wikipedia (general knowledge)
  - Wikidata (structured facts and rankings)
  - Calculator (safe arithmetic engine)

---

### ➗ Calculator Tool

- Safe AST-based arithmetic evaluator (no `eval`)
- Supports: `+ - * / % ** //` and parentheses
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
- Optimized for rankings and comparisons

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Get JWT access token |
| POST | `/chat` | Chat with AI agent |
| GET | `/health` | Service health check |
| GET | `/health/tools/{tool_name}` | Tool health check |

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

Create a `.env` file:

SECRET_KEY=your_secret_key_here  
GROQ_API_KEY=your_groq_api_key  
FAKE_USERNAME=admin  
FAKE_PASSWORD=password  

Generate secret key:

python -c "import secrets; print(secrets.token_hex(32))"

---

## ▶️ Run Application

uvicorn main:app --reload

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs  

---

## 🔐 Authentication Flow

1. Call `/login` with credentials  
2. Receive JWT token  
3. Send token in header: Authorization: Bearer <token>  
4. Access `/chat` endpoint  

---

## 🧠 How the Agent Works

User input flows through a structured pipeline:

User Input  
→ Phase 1: LLM plans tool usage  
→ Phase 2: Python executes tools safely from registry  
→ Phase 3: LLM synthesizes final grounded response  

This ensures:
- Deterministic execution
- Safe tool usage
- Reduced hallucination risk
- Full traceability of decisions

---

## 🏗️ Architecture

## 🧠 LLM Swap Resilience (Important Design Insight)

The system is intentionally model-agnostic with a lightweight safety layer to handle malformed outputs.

### 🔁 What happens if you change the LLM?

If the model is replaced or upgraded, the system remains stable because:

### ✔ The LLM only handles:
- Tool planning
- Response synthesis

### ✔ The system does NOT rely on the LLM for:
- Tool execution
- Mathematical correctness
- External data retrieval
- Safety validation

These are handled entirely by deterministic Python code and tools.

---

## ⚙️ Why the system remains stable

### 🧩 Deterministic layers
- Calculator (AST engine)
- Wikipedia API
- Wikidata API
- Tool registry
- Execution pipeline

### 🧠 LLM is a replaceable component
The model is a reasoning assistant, not a system controller.

---

## 🚨 What may change when swapping LLMs

### 📌 Tool selection quality
Better models → better tool usage decisions  
Weaker models → may skip tools or overuse direct answers  

### 📌 Query quality
Better models → more precise queries  
Weaker models → ambiguous queries  

### 📌 Response style
Tone may change, but grounding remains tool-based

---

## 🧠 Key Principle

> Intelligence can change, but execution correctness cannot.

---

## 🔥 Practical Implication

You can upgrade or replace the LLM without changing:
- tools
- architecture
- execution logic
- API layer

Only reasoning quality changes.

---

## 🟢 Structured Tool Agent

- Planner (LLM)
- Executor (Python)
- Synthesizer (LLM)

Key properties:
- No direct tool execution by LLM
- No ReAct loop
- Single-pass planning
- Fully traceable execution

---

## 💬 Example Requests

### No Tool Example

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

### Calculator Example

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
  ],
  "steps": [
    "plan=[{'name': 'calculator', 'query': '25 * 18 + 10'}]"
  ],
  "error_id": null
}

---

### Wikipedia Example

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
  ],
  "steps": [
    "plan=[{'name': 'wikipedia', 'query': 'Artificial intelligence'}]"
  ],
  "error_id": null
}

---

### Wikidata Example

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
  ],
  "steps": [
    "plan=[{'name': 'wikidata', 'query': '2028 Summer Olympics host city'}]"
  ],
  "error_id": null
}

---

## 🚀 Benefits

- Clean separation of concerns
- Fully extensible tool system
- Safe deterministic execution
- Reduced hallucinations via tool grounding
- Easy debugging and traceability

---

## 🚧 Current Limitations

- Stateless per request
- Single planning step
- No streaming responses
- Limited tool ecosystem

---

## 🚀 Future Improvements

- Conversation memory
- Streaming (SSE/WebSockets)
- Parallel tool execution
- Tool confidence scoring
- Caching layer
- Multi-step planning

---

## 📄 License

MIT License

---

## 🧠 Aha Moment: How This Agent Really Works

At the core of this system is a simple but powerful idea:

> **The LLM proposes what might make sense.  
> Your code decides what is actually allowed.**

Once you understand this split, everything else in agent design becomes much easier to reason about.

It explains:

- why tool validation is necessary  
- why JSON parsing exists at all  
- why a tool registry is important  
- why guardrails are not optional extras, but core design  

All of these are consequences of separating **suggestion (LLM)** from **enforcement (code)**.

---

## 🔧 What this changes in how you think

From this perspective, the system stops being “an AI that does everything” and becomes a structured pipeline:

- The LLM explores possibilities
- The code enforces rules and safety
- Tools execute real, deterministic actions

---

## 🚀 Why this matters

As you build further, this mental model helps you naturally see:

- where new tools should be added  
- where stricter safety checks are needed  
- where the LLM is useful  
- and where it should never be trusted directly  

---

## 🧭 Key Insight

This separation between **suggestion and enforcement** is the foundation of reliable AI agents.

Once you see it, you can’t unsee it — and every part of the system starts to make sense from it.

---

## 🙌 Final Notes

This system is a structured tool-calling architecture where:
- tools are deterministic
- LLM is planner + narrator
- execution is fully controlled

It is designed for stability, debuggability, and safe extensibility.