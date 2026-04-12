from uuid import UUID

import pytest
from sqlalchemy.exc import NoResultFound

from src.security.password import verify_password
from src.users.model.requests import ChangePasswordRequest, UpdateUserRequest
from src.users.model.responses import (
    ChangePasswordResponse,
    UserResponse,
)
from src.entities.user import User
from src.errors.custom import AuthenticationError, InvalidPasswordConfirmError
from src.users.service.user_service import (
    change_password,
    delete_user,
    get_user,
    get_all_users,
    update_user_name,
)


def test_get_user(db_session, _test_user, test_user_id):
    found_user = get_user(UUID(test_user_id), db_session)

    assert found_user.email == _test_user.email


def test_get_all_users(db_session, _two_users, test_user_data, test_user_2_data):
    users = get_all_users(db_session)

    user_emails = [user.email for user in users]

    assert test_user_data.email in user_emails
    assert test_user_2_data.email in user_emails


def test_get_nonexisting_user_fails(db_session):
    random_user_id = UUID("3cbdc1b9-5f63-4d79-8a73-1d1d8e6a0d6f")

    with pytest.raises(NoResultFound):
        get_user(random_user_id, db_session)


def test_delete_user(_test_user, test_user_id, db_session):
    delete_user(UUID(test_user_id), db_session)

    with pytest.raises(NoResultFound):
        get_user(UUID(test_user_id), db_session)


def test_delete_nonexisting_user_fails(db_session):
    random_user_id = UUID("3cbdc1b9-5f63-4d79-8a73-1d1d8e6a0d6f")

    with pytest.raises(NoResultFound):
        delete_user(random_user_id, db_session)


def test_update_user_name(db_session, _test_user, test_user_data, test_user_id):
    new_user_first_name = "New"
    new_user_last_name = "Name"

    assert update_user_name(
        UpdateUserRequest(first_name=new_user_first_name, last_name=new_user_last_name),
        UUID(test_user_id),
        db_session,
    ) == UserResponse(
        id=test_user_id,
        email=test_user_data.email,
        first_name=new_user_first_name,
        last_name=new_user_last_name,
    )


def test_update_nonexisting_user_name_fails(db_session, _test_user):
    new_user_first_name = "New"
    new_user_last_name = "Name"

    random_user_id = UUID("3cbdc1b9-5f63-4d79-8a73-1d1d8e6a0d6f")

    with pytest.raises(NoResultFound):
        update_user_name(
            UpdateUserRequest(
                first_name=new_user_first_name, last_name=new_user_last_name
            ),
            random_user_id,
            db_session,
        )


def test_update_user_name_missing_parameter_fails(db_session, _test_user, test_user_id):
    new_user_first_name = "New"
    new_user_last_name = ""

    with pytest.raises(ValueError) as exctext:
        update_user_name(
            UpdateUserRequest(
                first_name=new_user_first_name, last_name=new_user_last_name
            ),
            UUID(test_user_id),
            db_session,
        )
    assert str(exctext.value) == "Missing required parameter"


def test_change_password(db_session, _test_user, test_user_data, test_user_id):
    new_user = db_session.get(User, UUID(test_user_id))
    new_password = "updated-pass"
    change_password_request = ChangePasswordRequest(
        current_password=test_user_data.password,
        new_password=new_password,
        new_password_confirm=new_password,
    )

    assert change_password(
        change_password_request, UUID(test_user_id), db_session
    ) == ChangePasswordResponse(message="Password successfully changed")
    assert verify_password(new_password, new_user.hashed_password)


def test_change_password_fails_wrong_confirm(
    db_session, _test_user, test_user_data, test_user_id
):
    new_password = "updated-pass"
    wrong_new_pass = "wrong_pass"

    change_password_request = ChangePasswordRequest(
        current_password=test_user_data.password,
        new_password=new_password,
        new_password_confirm=wrong_new_pass,
    )

    with pytest.raises(InvalidPasswordConfirmError) as excinfo:
        change_password(change_password_request, UUID(test_user_id), db_session)

    assert str(excinfo.value) == "Confirm password doesn't match new password"


def test_change_password_wrong_current_password_fails(
    db_session, _test_user, test_user_id
):
    new_password = "updated-pass"
    wrong_currrent_password = "wrong_pass"

    change_password_request = ChangePasswordRequest(
        current_password=wrong_currrent_password,
        new_password=new_password,
        new_password_confirm=new_password,
    )
    with pytest.raises(AuthenticationError):
        change_password(change_password_request, UUID(test_user_id), db_session)
