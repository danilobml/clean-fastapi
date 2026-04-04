from src.entities.user import User
from src.models.token import TokenData
from src.services.auth_service import (
    authenticate_user,
    get_hashed_password,
    verify_token
)

def test_authenticate_user_success(db_session):
    user = User(
        first_name="Dan",
        last_name="Bar",
        email="dan@test.com",
        hashed_password=get_hashed_password("hashed"),
    )

    db_session.add(user)
    db_session.commit()

    assert authenticate_user("dan@test.com", "hashed", db_session) == user

def test_verify_token():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QG1haWwuY29tIiwiaWQiOiJhNGM4YTcyZS0zZjFkLTRiNmEtYjhjNS02YzBiOGYyZDdlOWEiLCJleHAiOjE3NzUzMzgwNTV9.cqg67JEakWaiZq8pCOw3PJ76zTlacznVHcgnHAZvWic"
    
    data = TokenData(user_id="a4c8a72e-3f1d-4b6a-b8c5-6c0b8f2d7e9a")
    
    assert verify_token(token) == data

