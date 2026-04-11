from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class ChangePasswordResponse(BaseModel):
    message: str


class DeleteUserResponse(BaseModel):
    message: str
