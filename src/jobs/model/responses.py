from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: UUID
    user_id: UUID
    description: str
    due_date: datetime
    priority: str
    is_completed: bool
