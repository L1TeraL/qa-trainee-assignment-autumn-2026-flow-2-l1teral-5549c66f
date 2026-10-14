import uuid

from api.client import APIClient


def test_protected_endpoints_require_auth():
    client = APIClient()

    item_id = "550e8400-e29b-41d4-a716-446655440000"
    seller_id = 123

    responses = [
        client.create_item(
            seller_id=seller_id,
            name="Unauthorized item",
            price=1000,
            statistics={
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        ),
        client.get_item(item_id),
        client.get_seller_items(seller_id),
        client.get_statistics_v1(item_id),
        client.get_statistics_v2(item_id),
        client.delete_item(item_id),
    ]

    for response in responses:
        assert response.status_code == 401


def test_invalid_token_rejected():
    client = APIClient()
    client.token = "invalid_token"

    item_id = "550e8400-e29b-41d4-a716-446655440000"

    responses = [
        client.get_item(item_id),
        client.get_seller_items(123),
        client.get_statistics_v1(item_id),
        client.get_statistics_v2(item_id),
        client.delete_item(item_id),
    ]

    for response in responses:
        assert response.status_code == 401


def test_seller_id_cannot_be_spoofed(client, user):
    another_username = f"another_user_{uuid.uuid4().hex[:8]}"

    register_response = client.register(
        another_username,
        "qwerty123",
    )

    assert register_response.status_code == 201

    another_user_id = register_response.json()["id"]

    response = client.create_item(
        seller_id=another_user_id,
        name="Spoofed seller item",
        price=1000,
        statistics={
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 400
