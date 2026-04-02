from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: UUID | None = None
    
    def get_uuid(self) -> UUID | None:
        return self.user_id
