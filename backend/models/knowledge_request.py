from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class KnowledgeRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None