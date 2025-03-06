from pydantic import BaseModel


class SQLRequest(BaseModel):
    description: str
    dialect: str = "MySQL"