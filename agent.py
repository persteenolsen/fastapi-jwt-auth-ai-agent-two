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
    model="openai/gpt-oss-120b",
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
# SAFE JSON PARSER (IMPROVED ONLY)
# ------------------------------
def safe_json_load(text: str) -> Dict[str, Any]:
    try:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            logger.warning("No JSON object found in LLM output")
            logger.debug(f"Raw output:\n{text}")
            return {"tools": []}

        candidate = text[start:end + 1]

        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}")
            logger.debug(f"Bad JSON:\n{candidate}")
            return {"tools": []}

        if not isinstance(data, dict):
            logger.warning("JSON root is not an object")
            return {"tools": []}

        tools = data.get("tools")

        if not isinstance(tools, list):
            logger.warning("Missing or invalid 'tools' list")
            return {"tools": []}

        cleaned_tools = []

        for i, t in enumerate(tools):
            if not isinstance(t, dict):
                logger.warning(f"Tool[{i}] invalid: {t}")
                continue

            name = t.get("name")
            query = t.get("query")

            if not isinstance(name, str) or not isinstance(query, str):
                logger.warning(f"Tool[{i}] malformed: {t}")
                continue

            name = name.strip()
            query = query.strip()

            if not name or not query:
                continue

            cleaned_tools.append({
                "name": name,
                "query": query
            })

        return {"tools": cleaned_tools}

    except Exception:
        logger.exception("Unexpected error in safe_json_load")
        return {"tools": []}

# ------------------------------
# NORMALIZATION
# ------------------------------
def normalize(text: str) -> str:
    return text.strip().replace("\u00a0", "").replace("\n", "")

# ------------------------------
# MATH DETECTION
# ------------------------------
def is_math_query(text: str) -> bool:
    text = normalize(text)
    has_operator = any(op in text for op in ["+", "-", "*", "/", "%", "**", "(", ")"])
    if not has_operator:
        return False
    allowed_chars = set("0123456789+-*/%(). ")
    return all(c in text for c in allowed_chars)

# ------------------------------
# WIKIDATA REWRITE
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
# TOOL INFO
# ------------------------------
def build_tool_prompt() -> str:
    return "\n".join([
        "- wikipedia: general knowledge, explanations",
        "- wikidata: structured entities, facts, rankings",
        "- calculator: arithmetic, math expressions",
    ])

# ------------------------------
# SYNTHESIS
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
"""
    try:
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return "Could not synthesize an answer from the tools."

# =========================================================
# PHASE 1 — PLANNING
# =========================================================
def plan_tools(raw_input: str) -> List[Dict[str, Any]]:
    tool_prompt = f"""
You are a tool router. Decide which tools (if any) to use.

Available tools:
{build_tool_prompt()}

Rules:
- calculator ONLY for math
- wikipedia for explanations
- wikidata for structured facts
- return JSON only
- if casual: {{"tools": []}}

IMPORTANT:
- NEVER output tool execution formats
- NEVER output {{"name": "..."}}

Format:
{{
  "tools": [
    {{"name": "tool_name", "query": "query"}}
  ]
}}

Question:
{raw_input}
"""

    decision_text = llm.invoke(tool_prompt).content.strip()

    start = decision_text.find("{")
    end = decision_text.rfind("}")
    if start != -1 and end != -1 and end >= start:
        decision_text = decision_text[start:end + 1]

    decision = safe_json_load(decision_text)
    return decision.get("tools", [])

# =========================================================
# PHASE 2 — EXECUTION
# =========================================================
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

# =========================================================
# PHASE 3 — SYNTHESIS
# =========================================================
def synthesize(raw_input: str, verified_results: List[Dict[str, Any]]) -> str:
    if verified_results:
        return synthesize_answer(raw_input, verified_results)

    return llm.invoke(
        f"Answer clearly and concisely:\n{raw_input}"
    ).content.strip()

# =========================================================
# MAIN AGENT
# =========================================================
def run_agent(user_input: str) -> Dict[str, Any]:
    steps: List[str] = []
    tools_used: List[Dict[str, Any]] = []
    verified_results: List[Dict[str, Any]] = []

    try:
        raw_input = normalize(user_input)

        # FAST PATH: MATH
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

        # PHASE 1: PLAN
        tools_to_use = plan_tools(raw_input)
        steps.append(f"plan={tools_to_use}")

        # PHASE 2: EXECUTE
        execute_tools(tools_to_use, raw_input, tools_used, verified_results)

        # PHASE 3: SYNTHESIZE
        response = synthesize(raw_input, verified_results)

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