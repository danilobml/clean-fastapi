from uuid import UUID

from fastapi import Request, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import NoResultFound
from starlette import status

from src.db.core import DbSession
from src.users.model.responses import UserResponse
from src.rate_limiting import limiter
from src.users.service import user_service

user_router = APIRouter(prefix="/users")


@user_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
@limiter.limit("5/hour")
async def get_user(request: Request, id: UUID, db: DbSession) -> UserResponse:
    try:
        user = user_service.get_user(id, db)
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@user_router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
@limiter.limit("5/hour")
async def get_all_users(request: Request, db: DbSession) -> list[UserResponse]:
    users_resp = []
    try:
        users = user_service.get_all_users(db)
        for user in users:
            users_resp.append(
                UserResponse(
                    id=str(user.id),
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )
            )
        return users_resp
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@user_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request, id: UUID, db: DbSession) -> None:
    try:
        user_service.delete_user(id, db)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
