from pydantic import BaseModel


class KnowledgeRequest(BaseModel):
    question: str