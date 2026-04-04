import pytest

from src.auth.model.requests import RegisterUserRequest
from src.entities.user import User
from src.auth.model.token import TokenData
from src.auth.service.auth_service import (
    authenticate_user,
    get_hashed_password,
    get_user,
    register_user,
    verify_token
)

def test_register_user(db_session):
    request = RegisterUserRequest(email="test@mail.com", password="test-pass", first_name="Tester", last_name="Testman")

    try:
        register_user(request, db_session) 
    except Exception as e:
        pytest.fail(f"register_user test failed: {e}")
    
    user = db_session.query(User).filter(User.email == request.email).one()
    
    assert user.first_name == request.first_name

def test_get_user(db_session):
    user = User(
        first_name="Dan",
        last_name="Bar",
        email="dan@test.com",
        hashed_password=get_hashed_password("hashed"),
    )
    db_session.add(user)
    db_session.commit()
    
    found_user = get_user(user.id, db_session)
    
    assert found_user.email == user.email


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

