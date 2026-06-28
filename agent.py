import json
import logging
import traceback
from typing import Any, Dict, List

from langchain_groq import ChatGroq
from config import GROQ_API_KEY

from tools.wikipedia import wikipedia_tool, wikidata_tool
from tools.calculator import calculator_tool

logger = logging.getLogger(__name__)

# ------------------------------
# LLM
# ------------------------------
llm = ChatGroq(

    # 27-06-2026 - Will soon be out of service by Groq.
    # Instead the below two models are recomended by Groq
    #model="llama-3.3-70b-versatile",
    
    # 27-06-2026 - Recomended by Groq but not working with my agent.py!
    # I belive the <think> is causing strange response
    #model="qwen/qwen3.6-27b",
    
    # 27-06-2026 - Recomended by Groq and now used!
    model="openai/gpt-oss-20b",

    temperature=0,
    api_key=GROQ_API_KEY,
)

# ------------------------------
# TOOL REGISTRY
# ------------------------------
TOOL_REGISTRY = {
    "wikipedia": wikipedia_tool,
    "wikidata": wikidata_tool,
    "calculator": calculator_tool,
}

# ------------------------------
# SAFE JSON PARSER
# ------------------------------
def safe_json_load(text: str) -> Dict[str, Any]:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}

# ------------------------------
# NORMALIZE INPUT
# ------------------------------
def normalize(text: str) -> str:
    return text.strip().replace("\u00a0", "").replace("\n", "")

# ------------------------------
# ROBUST MATH DETECTION
# ------------------------------
def is_math_query(text: str) -> bool:
    text = normalize(text)
    has_operator = any(op in text for op in ["+", "-", "*", "/", "%", "**", "(", ")"])
    if not has_operator:
        return False
    allowed_chars = set("0123456789+-*/%(). ")
    return all(c in allowed_chars for c in text)

# ------------------------------
# WIKIDATA QUERY REWRITE
# ------------------------------
def rewrite_for_wikidata(query: str) -> str:
    prompt = f"""
Convert this question into a simple Wikidata entity search query.

Rules:
- remove superlatives (largest, highest, most)
- keep only entity keywords
- return ONLY the query string

Question: {query}
"""
    try:
        return llm.invoke(prompt).content.strip()
    except Exception:
        return query

# ------------------------------
# TOOL PROMPT BUILDER
# ------------------------------
def build_tool_prompt() -> str:
    return "\n".join([
        "- wikipedia: general knowledge, explanations",
        "- wikidata: structured entities, facts, rankings",
        "- calculator: arithmetic, math expressions",
    ])

# ------------------------------
# SYNTHESIS PROMPT
# ------------------------------
def synthesize_answer(question: str, tool_data: List[Dict[str, Any]]) -> str:
    prompt = f"""
You are a precise assistant.

You MUST answer using ONLY the provided tool data.
Do NOT guess or add external knowledge.

If the data is incomplete, still explain clearly based on it.

Question:
{question}

Tool data:
{json.dumps(tool_data, indent=2)}

Return a natural, helpful explanation.
"""
    try:
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return "Could not synthesize an answer from the tools."


# ------------------------------
# HELPER FUNCTION - AGENT CORE
# ------------------------------ 
def execute_tools(
    tools_to_use: List[Dict[str, Any]],
    raw_input: str,
    tools_used: List[Dict[str, Any]],
    verified_results: List[Dict[str, Any]],
) -> None:
    for tool in tools_to_use:
        name = tool.get("name")
        query = tool.get("query", raw_input)
        tool_func = TOOL_REGISTRY.get(name)

        if not tool_func:
            tools_used.append({
                "tool": name,
                "query": query,
                "success": False,
            })
            continue

        try:
            if name == "wikidata":
                query = rewrite_for_wikidata(query)

            result = tool_func(query)
            success = bool(result.get("success", False))

            tools_used.append({
                "tool": name,
                "query": query,
                "success": success,
            })

            if success:
                verified_results.append(result)

        except Exception as e:
            logger.error(f"Tool error ({name}): {e}")
            tools_used.append({
                "tool": name,
                "query": query,
                "success": False,
            })

# ------------------------------
# AGENT CORE
# ------------------------------
def run_agent(user_input: str) -> Dict[str, Any]:
    steps: List[str] = []
    tools_used: List[Dict[str, Any]] = []
    verified_results: List[Dict[str, Any]] = []

    try:
        raw_input = normalize(user_input)

        # ------------------------------
        # 1. DIRECT MATH ROUTE
        # ------------------------------
        if is_math_query(raw_input):
            result = calculator_tool(raw_input)
            success = bool(result.get("success", False))
            tools_used.append({
                "tool": "calculator",
                "query": raw_input,
                "success": success,
            })
            if success:
                return {
                    "response": str(result["result"]),
                    "tools_used": tools_used,
                    "steps": ["direct_math_execution"],
                    "error_id": None,
                }

        # ------------------------------
        # 2. TOOL DECISION (safe, non-crashing version)
        # ------------------------------
        tool_prompt = f"""
You are a tool router. Decide which tools (if any) to use for a user question.

Available tools:
{build_tool_prompt()}

Rules:
- choose calculator ONLY for math
- choose wikipedia for factual questions
- choose wikidata for structured facts
- when using wikipedia, generate the most specific query possible
  to avoid ambiguous terms or disambiguation pages
- return JSON only
- If the question is conversational or casual, return exactly:
{{"tools": []}}

Formatting:
- Return ONLY JSON.
- JSON format:
{{
  "tools": [
    {{"name": "tool_name", "query": "query"}}
  ]
}}
- Do not include explanations, extra text, or emojis.

Examples:

Input: "hi"
Output: {{"tools": []}}

Input: "how are you?"
Output: {{"tools": []}}

Input: "2 + 2"
Output: {{"tools": [{{"name": "calculator", "query": "2 + 2"}}]}}

Input: "what is photosynthesis?"
Output: {{"tools": [{{"name": "wikipedia", "query": "photosynthesis"}}]}}

Input: "largest city in Germany by population"
Output: {{"tools": [{{"name": "wikidata", "query": "largest city in Germany"}}]}}

Question:
{raw_input}
"""
        decision_text = llm.invoke(tool_prompt).content.strip()
        decision = safe_json_load(decision_text)
        tools_to_use = decision.get("tools", [])
        steps.append(f"tool_plan={tools_to_use}")

        # ------------------------------
        # 3. EXECUTE TOOLS
        # ------------------------------
        execute_tools(tools_to_use, raw_input, tools_used, verified_results)

        # ------------------------------
        # 4. SYNTHESIZE FINAL ANSWER
        # ------------------------------
        if verified_results:
            response = synthesize_answer(raw_input, verified_results)
        else:
            # fallback
            response = llm.invoke(
                f"Answer clearly and concisely:\n{raw_input}"
            ).content.strip()

        return {
            "response": response,
            "tools_used": tools_used,
            "steps": steps,
            "error_id": None,
        }

    except Exception:
        logger.error(traceback.format_exc())
        return {
            "response": "Agent failed.",
            "tools_used": tools_used,
            "steps": steps,
            "error_id": "agent_exception",
        }