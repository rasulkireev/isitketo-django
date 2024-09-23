import base64

import environ
import requests

env = environ.Env()


class FatSecretClient:
    def __init__(self):
        self.client_id = env("FAT_SECRET_CLIENT_ID")
        self.client_secret = env("FAT_SECRET_CLIENT_SECRET")
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

    def make_api_request(self, endpoint, method="GET", params=None):
        if not self.access_token:
            self.get_access_token()

        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

        url = f"https://platform.fatsecret.com/rest/server.api{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=params)
        else:
            raise ValueError("Unsupported HTTP method")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.text}")


def search(query: str):
    client = FatSecretClient()
    token = client.get_access_token()

    search_params = {"search_expression": query, "format": "json"}
    res = requests.get(
        "https://platform.fatsecret.com/rest/foods/search/v1",
        params=search_params,
        headers={"Authorization": f"Bearer {token}"},
    )

    return res.json()["foods"]["food"]
