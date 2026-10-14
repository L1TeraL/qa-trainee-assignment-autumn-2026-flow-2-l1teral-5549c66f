import re
import uuid

import pytest

from api.client import APIClient


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(client):
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    password = "qwerty123"

    register_response = client.register(username, password)

    assert register_response.status_code == 201, (
        f"User registration failed: "
        f"{register_response.status_code} {register_response.text}"
    )

    user_data = register_response.json()

    authorize_response = client.authorize(username, password)

    assert authorize_response.status_code == 200, (
        f"User authorization failed: "
        f"{authorize_response.status_code} {authorize_response.text}"
    )

    return {
        "id": user_data["id"],
        "username": username,
        "password": password,
        "token": client.token,
    }


@pytest.fixture
def item(client, user):
    response = client.create_item(
        seller_id=user["id"],
        name=f"test_item_{uuid.uuid4().hex[:8]}",
        price=3007,
        statistics={
            "likes": 12,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 200, (
        f"Item creation failed: {response.status_code} {response.text}"
    )

    data = response.json()

    assert "status" in data

    match = re.search(
        r"[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[1-5][0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-"
        r"[0-9a-fA-F]{12}",
        data["status"],
    )

    assert match, f"Could not extract item UUID from response: {data}"

    item_id = match.group(0)

    yield {
        "id": item_id,
        "name": data.get("name"),
    }

    client.delete_item(item_id)
