from uuid import UUID

from starlette import status

from src.entities.user import User
from src.security.password import verify_password
from src.users.model.responses import UserResponse


def test_get_user_endpoint(client, _test_user, test_user_data, test_user_id):
    response = client.get(f"/users/{test_user_id}")

    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()

    UserResponse(**body)
    assert body["id"] == test_user_id
    assert body["first_name"] == test_user_data.first_name
    assert body["last_name"] == test_user_data.last_name
    assert body["email"] == test_user_data.email
    assert "hashed_password" not in body


def test_get_user_not_found(client, _test_user):
    non_existing_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    response = client.get(f"/users/{non_existing_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_users_endpoint(client, _two_users, test_user_data, test_user_2_data):
    response = client.get("/users")

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    returned_emails = sorted(user.get("email") for user in body)
    expected_emails = sorted([test_user_data.email, test_user_2_data.email])
    assert returned_emails == expected_emails


def test_delete_user_endpoint(client, _test_user, test_user_id):
    del_resp = client.delete(f"/users/{test_user_id}")
    get_resp = client.get(f"/users/{test_user_id}")

    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexisting_user_fails(client, _test_user):
    nonexisting_user_id = "b7f6c2a4-3c8f-4c1f-9d7a-2e6b5a9f8d13"

    response = client.delete(f"/users/{nonexisting_user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_name_endpoint(client, _test_user, test_user_id, db_session):
    new_first_name = "Updated"
    new_last_name = "Name"

    response = client.patch(
        f"/users/{test_user_id}",
        json={"first_name": new_first_name, "last_name": new_last_name},
    )

    updated_user = db_session.get(User, UUID(test_user_id))

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["first_name"] == new_first_name
    assert body["last_name"] == new_last_name

    assert updated_user.first_name == new_first_name
    assert updated_user.last_name == new_last_name


def test_update_nonexisting_user_name_fails(client, _test_user):
    new_first_name = "Updated"
    new_last_name = "Name"

    nonexisting_user_id = "b7f6c2a4-3c8f-4c1f-9d7a-2e6b5a9f8d13"

    response = client.patch(
        f"/users/{nonexisting_user_id}",
        json={"first_name": new_first_name, "last_name": new_last_name},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_name_missing_param_fails(client, _test_user, test_user_id):
    new_first_name = "Updated"
    new_last_name = ""

    response = client.patch(
        f"/users/{test_user_id}",
        json={"first_name": new_first_name, "last_name": new_last_name},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_change_password_endpoint(
    client, _test_user, test_user_data, test_user_id, db_session
):
    new_password = "new-pass"

    response = client.patch(
        f"/users/{test_user_id}/change-password",
        json={
            "current_password": test_user_data.password,
            "new_password": new_password,
            "new_password_confirm": new_password,
        },
    )

    body = response.json()

    user = db_session.get(User, UUID(test_user_id))

    assert response.status_code == status.HTTP_200_OK
    assert body.get("message") == "Password successfully changed"

    assert verify_password(new_password, user.hashed_password)


def test_change_password_wrong_id_fails(client, _test_user, test_user_data):
    new_password = "new-pass"
    nonexisting_user_id = "b7f6c2a4-3c8f-4c1f-9d7a-2e6b5a9f8d13"

    response = client.patch(
        f"/users/{nonexisting_user_id}/change-password",
        json={
            "current_password": test_user_data.password,
            "new_password": new_password,
            "new_password_confirm": new_password,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_change_password_wrong_password_fails(client, _test_user, test_user_id):
    new_password = "new-pass"
    wrong_password = "wrong-pass"

    response = client.patch(
        f"/users/{test_user_id}/change-password",
        json={
            "current_password": wrong_password,
            "new_password": new_password,
            "new_password_confirm": new_password,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_password_wrong_password_confirm_fails(
    client, _test_user, test_user_data, test_user_id
):
    new_password = "new-pass"
    wrong_password_confirm = "wrong-pass"

    response = client.patch(
        f"/users/{test_user_id}/change-password",
        json={
            "current_password": test_user_data.password,
            "new_password": new_password,
            "new_password_confirm": wrong_password_confirm,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
