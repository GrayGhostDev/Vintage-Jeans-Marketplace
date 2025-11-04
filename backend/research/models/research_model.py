from sqlmodel import SQLModel, Field
from datetime import datetime

class ResearchSummary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    client_name: str
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
