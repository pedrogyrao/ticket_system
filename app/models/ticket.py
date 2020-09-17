from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TicketModel(BaseModel):
    description: str
    points: int
    sprint_num: int
    handler: Optional[str] = None


class TicketModelInDB(TicketModel):
    _id: str
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class TicketPutModel(BaseModel):
    description: str = None
    points: int = None
    sprint_num: int = None
    handler: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
