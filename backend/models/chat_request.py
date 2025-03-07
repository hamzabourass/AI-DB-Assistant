"""Request models for chat operations."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Message(BaseModel):
    role: str
    content: str

class SaveChatRequest(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]
    title: Optional[str] = None

class GetChatRequest(BaseModel):
    conversation_id: str

class DeleteChatRequest(BaseModel):
    conversation_id: str

class ChatListRequest(BaseModel):
    limit: int = 20
    offset: int = 0

# Update KnowledgeRequest to include optional conversation_id
class KnowledgeRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None