import uuid

import allure

from api.client import APIClient


def test_full_item_lifecycle():
    client = APIClient()

    # Регистрация
    with allure.step("Регистрация пользователя"):
        username = f"e2e_user_{uuid.uuid4().hex[:8]}"
        password = "Qwerty123"

        register_response = client.register(username, password)

        assert register_response.status_code == 201, (
            f"Registration failed: "
            f"{register_response.status_code} {register_response.text}"
        )

        user = register_response.json()

        assert "id" in user
        seller_id = user["id"]

    # Авторизация
    with allure.step("Авторизация пользователя"):
        auth_response = client.authorize(username, password)

        assert auth_response.status_code == 200, (
            f"Authorization failed: {auth_response.status_code} {auth_response.text}"
        )

        assert client.token

    # Создание объявления
    with allure.step("Создание объявления"):
        create_response = client.create_item(
            seller_id=seller_id,
            name="Test item",
            price=1000,
            statistics={
                "likes": 10,
                "viewCount": 20,
                "contacts": 5,
            },
        )

        assert create_response.status_code == 200, (
            f"Item creation failed: "
            f"{create_response.status_code} {create_response.text}"
        )

        data = create_response.json()

        assert "status" in data

        item_id = data["status"].split()[-1]

    try:
        # Получение объявления
        with allure.step("Получение объявления"):
            get_response = client.get_item(item_id)

            assert get_response.status_code == 200

            items = get_response.json()

            assert isinstance(items, list)
            assert len(items) == 1

            item = items[0]

            assert item["id"] == item_id
            assert item["sellerId"] == seller_id
            assert item["name"] == "Test item"
            assert item["price"] == 1000

        # Статистика v1
        with allure.step("Получение статистики v1"):
            stats_v1_response = client.get_statistics_v1(item_id)

            assert stats_v1_response.status_code == 200

            stats_v1 = stats_v1_response.json()

            assert isinstance(stats_v1, list)
            assert len(stats_v1) == 1

        # Статистика v2
        with allure.step("Получение статистики v2"):
            stats_v2_response = client.get_statistics_v2(item_id)

            assert stats_v2_response.status_code in (100, 200)

            stats_v2 = stats_v2_response.json()

            assert stats_v2 is not None

        # Удаление объявления
        with allure.step("Удаление объявления"):
            delete_response = client.delete_item(item_id)

            assert delete_response.status_code in (200, 204)

        # Проверка удаления
        with allure.step("Проверка удаления объявления"):
            get_after_delete_response = client.get_item(item_id)

            assert get_after_delete_response.status_code == 404

    finally:
        with allure.step("Очистка тестовых данных"):
            client.delete_item(item_id)
