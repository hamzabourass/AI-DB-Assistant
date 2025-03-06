from pydantic import BaseModel


class HistoryDeleteRequest(BaseModel):
    history_id: int