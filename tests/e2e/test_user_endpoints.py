from uuid import UUID

from starlette import status

from src.entities.user import User
from src.security.password import get_hashed_password
from src.users.model.responses import UserResponse


def test_get_user_endpoint(client, test_user_data, test_user_id, db_session):
    user = User(
        id=UUID(test_user_id),
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    db_session.add(user)
    db_session.commit()

    response = client.get(f"/users/{test_user_id}")

    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()

    UserResponse(**body)
    assert body["id"] == test_user_id
    assert body["first_name"] == test_user_data.first_name
    assert body["last_name"] == test_user_data.last_name
    assert body["email"] == test_user_data.email
    assert "hashed_password" not in body


def test_get_user_not_found(client, test_user_data, test_user_id, db_session):
    user = User(
        id=UUID(test_user_id),
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    db_session.add(user)
    db_session.commit()

    non_existing_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    response = client.get(f"/users/{non_existing_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_users_endpoint(client, test_user_data, test_user_2_data, db_session):
    user_1 = User(
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    user_2 = User(
        first_name=test_user_2_data.first_name,
        last_name=test_user_2_data.last_name,
        email=test_user_2_data.email,
        hashed_password=get_hashed_password(test_user_2_data.password),
    )
    db_session.add(user_1)
    db_session.add(user_2)
    db_session.commit()

    response = client.get("/users")

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    returned_emails = sorted(user.get("email") for user in body)
    expected_emails = sorted([user_1.email, user_2.email])
    assert returned_emails == expected_emails


def test_delete_user_endpoint(client, test_user_data, test_user_id, db_session):
    user = User(
        id=UUID(test_user_id),
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    db_session.add(user)
    db_session.commit()

    del_resp = client.delete(f"/users/{test_user_id}")
    get_resp = client.get(f"/users/{test_user_id}")

    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
