import requests


class APIClient:
    BASE_URL = "https://qa-internship.avito.com"

    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def register(self, username, password):
        return self.session.post(
            f"{self.BASE_URL}/api/1/register",
            json={
                "username": username,
                "password": password,
            },
        )

    def authorize(self, username, password):
        response = self.session.post(
            f"{self.BASE_URL}/api/1/autorize",
            json={
                "username": username,
                "password": password,
            },
        )

        if response.status_code == 200:
            self.token = response.json()["accessToken"]

        return response

    def _auth_headers(self):
        if not self.token:
            return {}

        return {
            "Authorization": f"Bearer {self.token}",
        }

    def create_item(self, seller_id, name, price, statistics):
        return self.session.post(
            f"{self.BASE_URL}/api/1/item",
            headers=self._auth_headers(),
            json={
                "sellerID": seller_id,
                "name": name,
                "price": price,
                "statistics": statistics,
            },
        )

    def get_item(self, item_id):
        return self.session.get(
            f"{self.BASE_URL}/api/1/item/{item_id}",
            headers=self._auth_headers(),
        )

    def get_seller_items(self, seller_id):
        return self.session.get(
            f"{self.BASE_URL}/api/1/{seller_id}/item",
            headers=self._auth_headers(),
        )

    def get_statistics_v1(self, item_id):
        return self.session.get(
            f"{self.BASE_URL}/api/1/statistic/{item_id}",
            headers=self._auth_headers(),
        )

    def get_statistics_v2(self, item_id):
        return self.session.get(
            f"{self.BASE_URL}/api/2/statistic/{item_id}",
            headers=self._auth_headers(),
        )

    def delete_item(self, item_id):
        return self.session.delete(
            f"{self.BASE_URL}/api/2/item/{item_id}",
            headers=self._auth_headers(),
        )
