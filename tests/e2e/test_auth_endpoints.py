from starlette import status

def test_register_and_login(client, test_user_data):
    register_response = client.post(
        "/auth/register",
        json={
            "email": test_user_data.email,
            "password": test_user_data.password,
            "first_name": test_user_data.first_name,
            "last_name": test_user_data.last_name,
        },
    )
    assert register_response.status_code == status.HTTP_201_CREATED, register_response.text

    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data.email,
            "password": test_user_data.password,
        },
    )

    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
