import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Date, String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from ..db.core import Base


class Priority(enum.Enum):
    low = 0
    medium = 1
    high = 2


class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    description = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), nullable=False, default=Priority.medium)
    is_completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(Date, default=datetime.now())
    updated_at = Column(Date, default=datetime.now())
    
    def __repr__(self):
        return f"<Job(description:{self.description}, due_date:{self.due_date}, completed: {self.is_completed})>"
