import base64

import requests

from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)


class FatSecretClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://oauth.fatsecret.com/connect/token"
        self.access_token = None

    def get_access_token(self):
        if self.access_token:
            return self.access_token

        # Encode client_id and client_secret
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {"Authorization": f"Basic {encoded_credentials}", "Content-Type": "application/x-www-form-urlencoded"}

        data = {"grant_type": "client_credentials", "scope": "basic"}

        response = requests.post(self.base_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to obtain access token: {response.text}")

    def search(self, query: str):
        logger.info(
            "Searching FatSecret Database",
            query=query,
        )
        if not self.access_token:
            self.get_access_token()

        res = requests.get(
            "https://platform.fatsecret.com/rest/foods/search/v1",
            params={"search_expression": query, "format": "json"},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return res.json()["foods"]["food"]

    def get_product_info(self, food_id):
        logger.info("Getting Detailed Product Info from Fatsecret", food_id=food_id)
        if not self.access_token:
            self.get_access_token()

        res = requests.get(
            "https://platform.fatsecret.com/rest/food/v4",
            params={"food_id": food_id, "include_food_images": "true", "format": "json"},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return res.json()["food"]
