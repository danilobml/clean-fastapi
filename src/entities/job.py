import uuid
import enum
from sqlalchemy import Column, ForeignKey, DateTime, String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db.core import Base


class Priority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    description = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), nullable=False, default=Priority.medium)
    is_completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Job(description:{self.description}, due_date:{self.due_date}, completed: {self.is_completed})>"
