import logging
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.entities.user import User
from src.models.requests import RegisterUserRequest
from src.services.auth_service import get_hashed_password
from ..db.core import Session


def register_user(request: RegisterUserRequest, db: Session) -> None:
    try:
        user = User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            hashed_password=get_hashed_password(request.password),
        )
        db.add(user)
        db.commit()
    except Exception as e:
        logging.warning(f"Failed to register user with email {user.email}: {e}")
        raise

def get_user(id: UUID, db: Session) -> User:
    try:
        user = db.query(User).filter(User.id == id).one()
        return user
    except NoResultFound as e:
        logging.warning(f"No user found with id {id}: {e}")
        raise
