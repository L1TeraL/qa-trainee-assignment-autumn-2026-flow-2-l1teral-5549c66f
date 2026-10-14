import uuid

from api.client import APIClient


def test_authorize_success():
    client = APIClient()

    username = f"auth_user_{uuid.uuid4().hex[:8]}"
    password = "Qwerty123"

    register_response = client.register(username, password)

    assert register_response.status_code == 201

    response = client.authorize(username, password)

    assert response.status_code == 200

    data = response.json()

    assert "accessToken" in data
    assert data["accessToken"]
    assert data["tokenType"] == "Bearer"


def test_authorize_wrong_password():
    client = APIClient()

    username = f"auth_user_{uuid.uuid4().hex[:8]}"
    password = "Qwerty123"

    register_response = client.register(username, password)

    assert register_response.status_code == 201

    response = client.authorize(username, "WrongPassword123")

    assert response.status_code == 401


def test_authorize_nonexistent_user():
    client = APIClient()

    username = f"nonexistent_user_{uuid.uuid4().hex[:8]}"

    response = client.authorize(
        username,
        "Qwerty123",
    )

    assert response.status_code == 401


def test_authorize_without_username():
    client = APIClient()

    response = client.session.post(
        f"{client.BASE_URL}/api/1/autorize",
        json={
            "password": "Qwerty123",
        },
    )

    assert response.status_code == 400


def test_authorize_without_password():
    client = APIClient()

    username = f"auth_user_{uuid.uuid4().hex[:8]}"

    response = client.session.post(
        f"{client.BASE_URL}/api/1/autorize",
        json={
            "username": username,
        },
    )

    assert response.status_code == 400


def test_authorize_empty_credentials():
    client = APIClient()

    response = client.session.post(
        f"{client.BASE_URL}/api/1/autorize",
        json={
            "username": "",
            "password": "",
        },
    )

    assert response.status_code == 400
