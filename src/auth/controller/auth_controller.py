from typing import Annotated

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.errors.custom import AuthenticationError

from ...rate_limiting import limiter
from ...db.core import DbSession
from ..model.requests import RegisterUserRequest
from ..service.auth_service import register_user, login_for_access_token

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit('5/hour')
async def register(request: Request, db: DbSession, register_user_request: RegisterUserRequest):
    register_user(register_user_request, db)

@auth_router.post("/login")
@limiter.limit('5/hour')
async def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):       
    return login_for_access_token(form_data, db)
