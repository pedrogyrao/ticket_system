from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TicketModel(BaseModel):
    ticket_id: str
    description: str
    points: int
    sprint_num: int
    handler: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
