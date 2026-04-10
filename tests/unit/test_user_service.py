import pytest

from src.users.service.user_service import change_password
from src.users.model.requests import ChangePasswordRequest
from src.users.model.responses import ChangePasswordResponse
from src.auth.service.auth_service import get_hashed_password
from src.entities.user import User
from src.errors.custom import InvalidPasswordConfirmError

def test_change_password(db_session, test_user_data):
    user = User(
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    db_session.add(user)
    db_session.commit()

    new_password = "updated-pass"

    change_password_request = ChangePasswordRequest(
        current_password=test_user_data.password,
        new_password=new_password,
        new_password_confirm=new_password,
    )

    assert change_password(change_password_request) == ChangePasswordResponse(message="success")
    assert user.hashed_password == get_hashed_password(new_password)


def test_change_password_fails_wrong_confirm(db_session, test_user_data):
    user = User(
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    db_session.add(user)
    db_session.commit()

    new_password = "updated-pass"
    wrong_new_pass = "wrong_pass"

    change_password_request = ChangePasswordRequest(
        current_password=test_user_data.password,
        new_password=new_password,
        new_password_confirm=wrong_new_pass,
    )
    with pytest.raises(InvalidPasswordConfirmError) as excinfo:
        change_password(change_password_request)
    
    assert str(excinfo.value) == "Confirm password doesn't match new password"
    assert user.hashed_password == get_hashed_password(test_user_data.password)
