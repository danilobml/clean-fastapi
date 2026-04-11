from datetime import timedelta, timezone
import logging
import os
from typing import Annotated
from uuid import UUID
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt

from src.auth.model.token import TokenData
from src.errors.custom import AuthenticationError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(email: str, user_id: UUID, expire_delta: timedelta) -> str:
    encode = {
        "sub": email,
        "id": str(user_id),
        "exp": datetime.now(timezone.utc) + expire_delta,
    }

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("id"))
        return TokenData(user_id=id)
    except jwt.PyJWTError as e:
        logging.warning(f"Failed to authenticate JWT: {e}")
        raise AuthenticationError()


def get_current_user(token: Annotated[str, Depends(oauth_bearer)]) -> TokenData:
    return verify_token(token)


CurrentUser = Annotated[TokenData, Depends(get_current_user)]
