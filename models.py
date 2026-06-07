from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ------------------------------
# AUTH MODELS
# ------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str

# ------------------------------
# CHAT MODELS
# ------------------------------
class ToolUsage(BaseModel):
    tool: str
    query: str
    success: bool = False

class ChatResponse(BaseModel):
    response: str
    tools_used: List[ToolUsage] = []
    steps: List[str] = []
    error_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str