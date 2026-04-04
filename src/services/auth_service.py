import os
import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from fastapi import Depends

from ..db.core import Session
from ..entities.user import User
from ..models.token import TokenData
from ..errors.custom import AuthenticationError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

bcrypt_context = CryptContext(schemes=['bcrypt'])
oauth_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def get_hashed_password(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(password, hashed_password)

def authenticate_user(email: str, password: str, db: Session) -> bool:    
    user = db.query(User).filter(User.email == email).one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        logging.warning(f"Failed to find user with email {email}")
        return False
    
    return True

def create_access_token(email: str, user_id: UUID, expire_delta: timedelta) -> str:
    encode = {
        "sub": email,
        "id": user_id,
        "exp": datetime.now(timezone.utc) + expire_delta
    }
    
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("id"))
        return TokenData(user_id=id)
    except PyJWTError as e:
        logging.warning(f"Failed to authenticate JWT: {e}")
        raise AuthenticationError()

def get_current_user(token: Annotated[str, Depends(oauth_bearer)]) -> TokenData:
    return verify_token(token)

CurrentUser = Annotated[TokenData, Depends(get_current_user)]
