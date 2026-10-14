import uuid

from api.client import APIClient


def test_register_success():
    client = APIClient()

    username = f"test_user_{uuid.uuid4().hex[:8]}"
    password = "Qwerty123"

    response = client.register(username, password)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert "username" in data
    assert data["username"] == username
    assert isinstance(data["id"], int)


def test_register_duplicate_username():
    client = APIClient()

    username = f"test_user_{uuid.uuid4().hex[:8]}"
    password = "Qwerty123"

    first_response = client.register(username, password)

    assert first_response.status_code == 201, (
        f"First registration failed: {first_response.status_code} {first_response.text}"
    )

    second_response = client.register(username, password)

    assert second_response.status_code == 409, (
        f"Expected 409 for duplicate username "
        f"{second_response.status_code} {second_response.text}"
    )


def test_register_without_username():
    client = APIClient()

    response = client.session.post(
        f"{client.BASE_URL}/api/1/register",
        json={
            "password": "Qwerty123",
        },
    )

    assert response.status_code == 400


def test_register_without_password():
    client = APIClient()

    username = f"test_user_{uuid.uuid4().hex[:8]}"

    response = client.session.post(
        f"{client.BASE_URL}/api/1/register",
        json={
            "username": username,
        },
    )

    assert response.status_code == 400


def test_register_empty_username():
    client = APIClient()

    response = client.register(
        "",
        "Qwerty123",
    )

    assert response.status_code == 400


def test_register_empty_password():
    client = APIClient()

    username = f"test_user_{uuid.uuid4().hex[:8]}"

    response = client.register(
        username,
        "",
    )

    assert response.status_code == 400


def test_register_invalid_username_type():
    client = APIClient()

    response = client.session.post(
        f"{client.BASE_URL}/api/1/register",
        json={
            "username": 12345,
            "password": "Qwerty123",
        },
    )

    assert response.status_code == 400


def test_register_invalid_password_type():
    client = APIClient()

    username = f"test_user_{uuid.uuid4().hex[:8]}"

    response = client.session.post(
        f"{client.BASE_URL}/api/1/register",
        json={
            "username": username,
            "password": 12345,
        },
    )

    assert response.status_code == 400
