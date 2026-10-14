import re
import uuid

from api.client import APIClient


def test_create_item_success(client, user):
    response = client.create_item(
        seller_id=user["id"],
        name="test_item",
        price=1000,
        statistics={
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "Сохранили объявление" in data["status"]


def extract_item_id(response):
    status = response.json()["status"]

    match = re.search(
        r"[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[1-5][0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-"
        r"[0-9a-fA-F]{12}",
        status,
    )

    assert match, f"Could not extract UUID from response: {status}"

    return match.group(0)


def test_create_items_have_unique_ids(client, user):
    item_ids = []

    try:
        response_1 = client.create_item(
            seller_id=user["id"],
            name="Test item 1",
            price=1000,
            statistics={
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        )

        assert response_1.status_code == 200

        item_id_1 = extract_item_id(response_1)
        item_ids.append(item_id_1)

        response_2 = client.create_item(
            seller_id=user["id"],
            name="Test item 2",
            price=2000,
            statistics={
                "likes": 20,
                "viewCount": 30,
                "contacts": 10,
            },
        )

        assert response_2.status_code == 200

        item_id_2 = extract_item_id(response_2)
        item_ids.append(item_id_2)

        assert item_id_1 != item_id_2

    finally:
        for item_id in item_ids:
            client.delete_item(item_id)


def test_create_items_with_same_data(client, user):
    item_ids = []

    item_data = {
        "seller_id": user["id"],
        "name": "Same test item",
        "price": 1500,
        "statistics": {
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    }

    try:
        response_1 = client.create_item(**item_data)
        assert response_1.status_code == 200

        item_id_1 = extract_item_id(response_1)
        item_ids.append(item_id_1)

        response_2 = client.create_item(**item_data)
        assert response_2.status_code == 200

        item_id_2 = extract_item_id(response_2)
        item_ids.append(item_id_2)

        assert item_id_1 != item_id_2

    finally:
        for item_id in item_ids:
            client.delete_item(item_id)


def test_create_item_without_auth():
    client = APIClient()

    response = client.create_item(
        seller_id=123,
        name="Unauthorized item",
        price=1000,
        statistics={
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 401


def test_create_item_with_invalid_token():
    client = APIClient()
    client.token = "invalid_token"

    response = client.create_item(
        seller_id=123,
        name="Invalid token item",
        price=1000,
        statistics={
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 401


def test_create_item_with_another_seller_id(client, user):
    another_user_response = client.register(
        f"another_user_{uuid.uuid4().hex[:8]}",
        "qwerty123",
    )

    assert another_user_response.status_code == 201

    another_user_id = another_user_response.json()["id"]

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


def test_create_item_without_seller_id(client, user):
    response = client.session.post(
        f"{client.BASE_URL}/api/1/item",
        headers=client._auth_headers(),
        json={
            "name": "Item without seller",
            "price": 1000,
            "statistics": {
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        },
    )

    assert response.status_code == 400


def test_create_item_without_name(client, user):
    response = client.session.post(
        f"{client.BASE_URL}/api/1/item",
        headers=client._auth_headers(),
        json={
            "sellerID": user["id"],
            "price": 1000,
            "statistics": {
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        },
    )

    assert response.status_code == 400


def test_create_item_without_price(client, user):
    response = client.session.post(
        f"{client.BASE_URL}/api/1/item",
        headers=client._auth_headers(),
        json={
            "sellerID": user["id"],
            "name": "Item without price",
            "statistics": {
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        },
    )

    assert response.status_code == 400


def test_create_item_with_invalid_price_type(client, user):
    response = client.session.post(
        f"{client.BASE_URL}/api/1/item",
        headers=client._auth_headers(),
        json={
            "sellerID": user["id"],
            "name": "Invalid price type",
            "price": "1000",
            "statistics": {
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        },
    )

    assert response.status_code == 400


def test_create_item_with_negative_price(client, user):
    response = client.session.post(
        f"{client.BASE_URL}/api/1/item",
        headers=client._auth_headers(),
        json={
            "sellerID": user["id"],
            "name": "Invalid price type",
            "price": -1,
            "statistics": {
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        },
    )

    assert response.status_code == 400, (
        "API позволяет создать объявление с отрицательной ценой: "
        f"{response.status_code} {response.text}"
    )


def test_create_item_with_negative_statistics(client, user):
    response = client.session.post(
        f"{client.BASE_URL}/api/1/item",
        headers=client._auth_headers(),
        json={
            "sellerID": user["id"],
            "name": "Negative statistics item",
            "price": 1000,
            "statistics": {
                "likes": -1,
                "viewCount": -1,
                "contacts": -1,
            },
        },
    )

    assert response.status_code == 400, (
        "API позволяет создать объявление с отрицательными значениями статистики: "
        f"{response.status_code} {response.text}"
    )


def test_create_item_with_negative_seller_id(client, user):
    response = client.session.post(
        f"{client.BASE_URL}/api/1/item",
        headers=client._auth_headers(),
        json={
            "sellerID": -1,
            "name": "Invalid price type",
            "price": 1000,
            "statistics": {
                "likes": 1,
                "viewCount": 1,
                "contacts": 1,
            },
        },
    )

    assert response.status_code == 400


def test_get_item_success(client, item):
    response = client.get_item(item["id"])

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1

    returned_item = data[0]

    assert returned_item["id"] == item["id"]


def test_get_nonexistent_item(client, user):
    nonexistent_item_id = "550e8400-e29b-41d4-a716-446655440000"

    response = client.get_item(nonexistent_item_id)

    assert response.status_code == 404


def test_get_item_with_invalid_uuid(client, user):
    response = client.get_item("dspifhufsidh")

    assert response.status_code == 400


def test_get_item_without_auth():
    client = APIClient()

    response = client.get_item("550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 401


def test_get_item_with_invalid_token():
    client = APIClient()
    client.token = "invalid_token"

    response = client.get_item("550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 401


def test_get_seller_items(client, user, item):
    response = client.get_seller_items(user["id"])

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    item_ids = [item["id"] for item in data]

    assert item["id"] in item_ids


def test_get_seller_item_empty(client, user):
    response = client.get_seller_items(user["id"])

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert data == []


def test_get_seller_items_without_auth():
    client = APIClient()

    response = client.get_seller_items(123)

    assert response.status_code == 401


def test_get_seller_items_with_invalid_seller_id(client, user):
    response = client.get_seller_items("invalid_seller_id")

    assert response.status_code == 400


def test_delete_item_success(client, user):
    response = client.create_item(
        seller_id=user["id"],
        name="Item to delete",
        price=1000,
        statistics={
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 200

    status = response.json()["status"]

    match = re.search(
        r"[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[1-5][0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-"
        r"[0-9a-fA-F]{12}",
        status,
    )

    assert match

    item_id = match.group(0)

    delete_response = client.delete_item(item_id)

    assert delete_response.status_code == 200


def test_get_item_after_delete(client, user):
    response = client.create_item(
        seller_id=user["id"],
        name="Item to delete",
        price=1000,
        statistics={
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 200

    item_id = extract_item_id(response)

    delete_response = client.delete_item(item_id)

    assert delete_response.status_code == 200

    get_response = client.get_item(item_id)

    assert get_response.status_code == 404


def test_delete_nonexistent_item(client, user):
    nonexistent_item_id = "550e8400-e29b-41d4-a716-446655440000"

    response = client.delete_item(nonexistent_item_id)

    assert response.status_code == 404


def test_delete_item_with_invalid_uuid(client, user):
    response = client.delete_item("not-a-valid-uuid")

    assert response.status_code == 400


def test_delete_item_without_auth():
    client = APIClient()

    response = client.delete_item("550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 401


def test_delete_item_with_invalid_token():
    client = APIClient()
    client.token = "invalid_token"

    response = client.delete_item("550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 401


def test_delete_item_twice(client, user):
    response = client.create_item(
        seller_id=user["id"],
        name="Item to delete twice",
        price=1000,
        statistics={
            "likes": 10,
            "viewCount": 20,
            "contacts": 5,
        },
    )

    assert response.status_code == 200

    item_id = extract_item_id(response)

    first_delete = client.delete_item(item_id)

    assert first_delete.status_code == 200

    second_delete = client.delete_item(item_id)

    assert second_delete.status_code == 404
