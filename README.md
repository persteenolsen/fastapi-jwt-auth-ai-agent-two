# 🚀 FastAPI AI Agent with Dynamic Tool Registry + JWT Auth + Groq LLM

A production-style AI Agent API built with FastAPI, featuring JWT authentication and a fully dynamic tool-calling architecture powered by Groq LLMs.

This project demonstrates a stable and extensible AI assistant built on a Tool Registry Agent Pattern, where tools are automatically exposed to the LLM, executed safely, and used to generate grounded responses.

# Version

At Render I use the PYTHON_VERSION environment variable to tell Render to use Python version 3.11. Locally I am using Python 3.12

---

## 📌 Project Info

- Version: 0.1.0
- Python: 3.11 / 3.12
- Architecture: Dynamic Tool Registry Agent (plan → execute → synthesize)
- Last Updated: 07-06-2026

---

## ✨ Key Features

### 🔐 Authentication
- JWT-based authentication (HS256)
- Protected `/chat` endpoint
- Token-based access control
- Environment-based credentials

---

### 🤖 AI Agent (Dynamic Tool System)
- LLM-driven tool selection from a dynamic registry
- No hardcoded tool list in prompts
- Tools auto-injected from `TOOL_REGISTRY`
- Execution pipeline: Plan → Execute → Synthesize
- Safe fallback to direct LLM response
- Protection against unknown tool execution

---

### 🧠 LLM Integration (Groq)
- Model: llama-3.3-70b-versatile
- High-speed inference via Groq API
- Temperature set to 0 for deterministic output
- Used for tool routing, query rewriting, and final synthesis

---

### 🧩 Tool Registry System
- Central `TOOL_REGISTRY` defines all tools
- LLM automatically receives tool list from registry
- Adding tools requires only creating the tool file and registering it
- Built-in tools:
  - Wikipedia 📚 (general knowledge)
  - Wikidata 🧾 (structured facts)
  - Calculator ➗ (safe arithmetic engine)

---

### ➗ Calculator Tool
- AST-based safe evaluator (no eval)
- Supports: +, -, *, /, %, **, // and parentheses
- Fully sandboxed execution
- Auto-used for pure math expressions

---

### 🌐 Wikipedia Tool
- Two-step retrieval:
  - Search API for entity lookup
  - REST summary API for content extraction
- Retry-enabled HTTP session
- Robust fallback handling

---

### 🧾 Wikidata Tool
- Entity search via Wikidata API
- LLM-assisted query simplification
- Optimized for structured facts and rankings

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | /login  | 🔐 Get JWT access token |
| POST   | /chat   | 💬 Chat with AI agent |
| GET    | /health | ❤️ Service health check |
| GET    | /health/tools | 🧩 All registered tools health |
| GET    | /health/tools/{tool_name} | 🔍 Single tool health check |

---

## ⚙️ Getting Started

### 1. Clone Repository
git clone https://github.com/your-username/your-repo.git  
cd your-repo  

### 2. 🐍 Create Virtual Environment
python -m venv venv  

Activate:

🪟 Windows  
venv\Scripts\activate  

🐧 Mac/Linux  
source venv/bin/activate  

### 3. 📦 Install Dependencies
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

🌐 API: http://127.0.0.1:8000  
📘 Docs: http://127.0.0.1:8000/docs  

---

## 🔐 Authentication Flow

1. Call `/login` with credentials  
2. Receive JWT token  
3. Send token in header: `Authorization: Bearer <token>`  
4. Access `/chat` endpoint  

---

## 🧠 How the Agent Works

User message → LLM reads available tools from registry → LLM generates tool plan → Registry validates tools → Tools execute safely → Results collected → LLM generates final grounded response  

---

## 🏗️ Architecture

### 🟢 Tool Registry Agent (Current System)

- Fully dynamic tool discovery  
- No hardcoded tool list in prompt  
- Safe execution via registry  
- Extensible plug-and-play tools  
- Deterministic execution pipeline  

### 🔵 Not ReAct

This system does not use ReAct.  
It does not:
- iterate reasoning step-by-step
- call tools in loops
- update reasoning after each tool call

Instead:

Plan → Execute → Synthesize

---

## 💬 Example Requests

### No tool example

POST /chat  
{  
  "message": "Tell me a joke"  
} 

{
  "response": "What do you call a fake noodle? An impasta.",
  "tools_used": [],
  "steps": [
    "tool_plan=[]"
  ],
  "error_id": null
}

---

### Calculator Example

POST /chat  
{  
  "message": "What is 25 * 18 + 10?"  
}  

{
  "response": "To calculate the result of the expression \"25 * 18 + 10\", we can follow the order of operations. First, we multiply 25 by 18, which equals 450. Then, we add 10 to this result, giving us a final answer of 460. This calculation is confirmed by the provided tool data from the calculator, which also yields a result of 460 for the expression \"25 * 18 + 10\". Therefore, the answer to the given expression is 460.",
  "tools_used": [
    {
      "tool": "calculator",
      "query": "25 * 18 + 10",
      "success": true
    }
  ],
  "steps": [
    "tool_plan=[{'name': 'calculator', 'query': '25 * 18 + 10'}]"
  ],
  "error_id": null
}

---

### Wikipedia Example

POST /chat  
{  
  "message": "What is Python?"  
}  

{
  "response": "According to the provided Wikipedia data, Python is a high-level, general-purpose programming language. It is designed to be easy to read and write, with a focus on simplicity and code readability. Python supports multiple programming styles, but it particularly emphasizes object-oriented programming and dynamic typing. Additionally, it has a comprehensive standard library and features like garbage collection, making it a versatile and user-friendly language.",
  "tools_used": [
    {
      "tool": "wikipedia",
      "query": "Python (programming language)",
      "success": true
    }
  ],
  "steps": [
    "tool_plan=[{'name': 'wikipedia', 'query': 'Python (programming language)'}]"
  ],
  "error_id": null
}

---

## 🚀 Benefits

- 🧩 Fully extensible tool system  
- 🧠 No prompt maintenance required when adding tools  
- 🛡️ Safe execution layer for all tools  
- 🧱 Clean separation of agent / tools / API  
- ⚙️ Production-ready FastAPI structure  
- 📊 Deterministic and debuggable behavior  

---

## 🚧 Current Limitations

- Stateless per request  
- Single-step planning only  
- No streaming responses yet  
- Limited tool ecosystem  

---

## 🚀 Future Improvements

- 🧠 Conversation memory  
- 🌊 Streaming responses (SSE/WebSockets)  
- ⚡ Parallel tool execution  
- 📊 Tool confidence scoring  
- 💾 Caching layer for Wikipedia/Wikidata  
- 🔗 Multi-step tool chaining  

---

## 📄 License

MIT License  

---

## 🙌 Final Notes

This project implements a modern dynamic tool registry architecture where tools are first-class citizens and the LLM dynamically adapts to available capabilities, enabling a scalable foundation for multi-tool AI systems.