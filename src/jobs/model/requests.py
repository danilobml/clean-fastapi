from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel

from src.entities.job import Priority


class CreateJobRequest(BaseModel):
    user_id: UUID
    description: str
    due_date: datetime
    priority: Optional[Priority] = None


class UpdateJobRequest(BaseModel):
    user_id: Optional[UUID] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
