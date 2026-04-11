import pytest

from src.auth.model.requests import RegisterUserRequest
from src.entities.user import User
from src.auth.model.token import TokenData
from src.security.jwt import verify_token
from src.security.password import get_hashed_password
from src.auth.service.auth_service import authenticate_user, register_user


def test_register_user(db_session):
    request = RegisterUserRequest(
        email="test@mail.com",
        password="test-pass",
        first_name="Tester",
        last_name="Testman",
    )

    try:
        register_user(request, db_session)
    except Exception as e:
        pytest.fail(f"register_user test failed: {e}")

    user = db_session.query(User).filter(User.email == request.email).one()

    assert user.first_name == request.first_name


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


def test_verify_token(test_token, test_user_id):
    data = TokenData(user_id=test_user_id)

    assert verify_token(test_token) == data
