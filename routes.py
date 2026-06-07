import time
import uuid
import logging
import traceback
from typing import Dict, Any

import requests
from fastapi import APIRouter, Depends, HTTPException

from models import LoginRequest, TokenResponse, ChatRequest, ChatResponse
from auth import create_access_token, verify_token
from config import FAKE_USERNAME, FAKE_PASSWORD

from agent import run_agent, TOOL_REGISTRY

logger = logging.getLogger(__name__)
router = APIRouter()

HEADERS = {"User-Agent": "fastapi-llm-agent/1.0"}

# ------------------------------
# LOGIN
# ------------------------------
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    if request.username != FAKE_USERNAME or request.password != FAKE_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": request.username})
    return TokenResponse(access_token=token)


# ------------------------------
# CHAT
# ------------------------------
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user: str = Depends(verify_token)):
    start = time.time()
    error_id = str(uuid.uuid4())

    try:
        logger.info(f"[USER={user}] {request.message}")

        result = run_agent(request.message)

        logger.info(f"Completed in {time.time() - start:.2f}s")

        return ChatResponse(
            response=result.get("response"),
            tools_used=result.get("tools_used", []),
            steps=result.get("steps", []),
            error_id=result.get("error_id"),
        )

    except Exception:
        logger.error(f"Error ID: {error_id}")
        logger.error(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail={
                "error_id": error_id,
                "message": "Agent execution failed",
            },
        )


# ------------------------------
# HEALTH
# ------------------------------
@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "fastapi-llm-agent",
        "agent": "tool-registry-v3",
        "tools_loaded": list(TOOL_REGISTRY.keys()),
    }


# ------------------------------
# TOOL HEALTH (DYNAMIC)
# ------------------------------
def _check_tool(tool_name: str, test_input: str = None) -> Dict[str, Any]:
    try:
        tool = TOOL_REGISTRY.get(tool_name)
        if not tool:
            return {"status": "missing"}
        
        # Use a valid math input for calculator
        if tool_name == "calculator":
            test_input = "1+1"
        else:
            test_input = test_input or "test"
            
        result = tool(test_input)

        return {
            "status": "ok" if result.get("success") else "fail",
            "tool": tool_name,
        }

    except Exception as e:
        return {
            "status": "fail",
            "tool": tool_name,
            "error": str(e),
        }


@router.get("/health/tools")
def health_tools():
    return {name: _check_tool(name) for name in TOOL_REGISTRY.keys()}


@router.get("/health/tools/{tool_name}")
def health_single_tool(tool_name: str):
    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail="Tool not found")

    return _check_tool(tool_name)