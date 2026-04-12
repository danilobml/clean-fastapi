import logging
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.entities.user import User
from src.security.password import get_hashed_password, verify_password

from ..model.requests import ChangePasswordRequest, UpdateUserRequest
from ..model.responses import ChangePasswordResponse, UserResponse
from src.errors.custom import InvalidPasswordConfirmError, AuthenticationError


def get_user(id: UUID, db: Session) -> User:
    try:
        user = db.query(User).filter(User.id == id).one()
        return user
    except NoResultFound as e:
        logging.warning(f"No user found with id {id}: {e}")
        raise


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def delete_user(id: UUID, db: Session) -> None:
    deleted = db.query(User).filter(User.id == id).delete()
    db.commit()

    if deleted == 0:
        logging.warning(f"Delete: Failed to find user with id {id}")
        raise NoResultFound()


def update_user_name(request: UpdateUserRequest, id: UUID, db: Session) -> UserResponse:
    if (
        not request.first_name
        or request.first_name == ""
        or not request.last_name
        or request.last_name == ""
    ):
        logging.warning("Update user name: missing parameter")
        raise ValueError("Missing required parameter")

    try:
        user = db.query(User).filter(User.id == id).one()

        user.first_name = request.first_name
        user.last_name = request.last_name

        db.commit()

        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    except NoResultFound as e:
        logging.warning(f"No user found with id {id}: {e}")
        raise


def change_password(
    request: ChangePasswordRequest, user_id: UUID, db: Session
) -> ChangePasswordResponse:
    if request.new_password != request.new_password_confirm:
        raise InvalidPasswordConfirmError()

    try:
        user = db.query(User).filter(User.id == user_id).one()
    except NoResultFound as e:
        logging.warning(f"No user found with id {user_id}: {e}")
        raise

    if not verify_password(request.current_password, user.hashed_password):
        raise AuthenticationError()

    user.hashed_password = get_hashed_password(request.new_password)

    db.commit()

    return ChangePasswordResponse(message="Password successfully changed")
