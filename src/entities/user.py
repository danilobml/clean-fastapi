import uuid
from datetime import datetime
from sqlalchemy import Column, Date, String
from sqlalchemy.dialects.postgresql import UUID
from ..db.core import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(Date, default=datetime.now())
    updated_at = Column(Date, default=datetime.now())
    
    def __repr__(self):
        return f"<User(name:{self.first_name} {self.last_name}, email:{self.email})>"
