from api.client import APIClient


def test_get_statistics_v1_success(client, item):
    response = client.get_statistics_v1(item["id"])

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1

    statistics = data[0]

    assert "likes" in statistics
    assert "viewCount" in statistics
    assert "contacts" in statistics


def test_get_statistics_v1_nonexistent_item(client, user):
    nonexistent_item_id = "550e8400-e29b-41d4-a716-446655440000"

    response = client.get_statistics_v1(nonexistent_item_id)

    assert response.status_code == 404


def test_get_statistics_v1_invalid_uuid(client, user):
    response = client.get_statistics_v1("not-a-valid-uuid")

    assert response.status_code == 400


def test_get_statistics_v1_without_auth():
    client = APIClient()
    response = client.get_statistics_v1("550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 401


def test_get_statistics_v2_success(client, item):
    response = client.get_statistics_v2(item["id"])

    assert response.status_code in (100, 200)

    data = response.json()

    assert data is not None


def test_get_statistics_v2_nonexistent_item(client, user):
    nonexistent_item_id = "550e8400-e29b-41d4-a716-446655440000"

    response = client.get_statistics_v2(nonexistent_item_id)

    assert response.status_code == 404


def test_get_statistics_v2_without_auth():
    client = APIClient()

    response = client.get_statistics_v2("550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 401


def test_get_statistics_v2_invalid_uuid(client, user):
    response = client.get_statistics_v2("not-a-valid-uuid")

    assert response.status_code == 404
