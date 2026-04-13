from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.entities.job import Priority


class JobResponse(BaseModel):
    id: UUID
    user_id: UUID
    description: str
    due_date: datetime
    priority: Priority
    is_completed: bool


class CreateJobResponse(BaseModel):
    id: UUID
    user_id: UUID
    description: str
    due_date: datetime
    priority: Priority


class CompleteJobResponse(BaseModel):
    message: str
