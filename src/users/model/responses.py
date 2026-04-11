from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str


class ChangePasswordResponse(BaseModel):
    message: str


class DeleteUserResponse(BaseModel):
    message: str
