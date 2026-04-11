import logging

import os
from datetime import timedelta
from typing import Annotated
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from src.auth.model.requests import RegisterUserRequest
from src.security.jwt import CurrentUser, create_access_token
from src.security.password import get_hashed_password, verify_password

from ...db.core import Session
from ...entities.user import User
from ..model.token import Token
from ...errors.custom import AuthenticationError

load_dotenv()


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


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
        logging.warning(f"Failed to register user with email {request.email}: {e}")
        raise


def authenticate_user(email: str, password: str, db: Session) -> User | None:
    user = db.query(User).filter(User.email == email).one_or_none()

    if user is None or not verify_password(password, user.hashed_password):
        logging.warning(f"Failed to find user with email {email}")
        return None

    return user


def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends(CurrentUser)], db: Session
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthenticationError()

    token = create_access_token(
        user.email, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=token, token_type="bearer")
