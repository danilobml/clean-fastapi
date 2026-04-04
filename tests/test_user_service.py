import pytest

from src.entities.user import User
from src.models.requests import RegisterUserRequest
from src.services.auth_service import get_hashed_password
from src.services.user_service import register_user, get_user


def test_register_user(db_session):
    request = RegisterUserRequest(email="test@mail.com", password="test-pass", first_name="Tester", last_name="Testman")

    try:
        register_user(request, db_session) 
    except Exception as e:
        pytest.fail("register_user test failed: {e}")
    
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
