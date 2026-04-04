import uuid
import enum
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..db.base import Base


class Priority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    priority: Mapped[Priority] = mapped_column(
        Enum(Priority),
        nullable=False,
        default=Priority.medium,
    )

    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<Job(description:{self.description}, "
            f"due_date:{self.due_date}, completed:{self.is_completed})>"
        )
