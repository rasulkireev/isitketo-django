import base64
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import RequestException

from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)


class FatSecretError(Exception):
    """Base exception for FatSecret related errors"""

    pass


class FatSecretAuthError(FatSecretError):
    """Authentication related errors"""

    pass


class FatSecretAPIError(FatSecretError):
    """API related errors"""

    pass


class FatSecretClient:
    BASE_URL = "https://oauth.fatsecret.com/connect/token"
    API_BASE_URL = "https://platform.fatsecret.com/rest"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Helper method to make HTTP requests with proper error handling and logging
        """
        try:
            url = f"{self.API_BASE_URL}/{endpoint}"

            if not headers and self.access_token:
                headers = {"Authorization": f"Bearer {self.access_token}"}

            logger.debug("[FatSecret] Making API request", method=method, endpoint=endpoint, params=params)

            response = requests.request(method=method, url=url, params=params, data=data, headers=headers)

            logger.debug(
                "[FatSecret] Received API response",
                status_code=response.status_code,
                endpoint=endpoint,
                response_length=len(response.text),
            )

            response.raise_for_status()

            return response.json()

        except RequestException as e:
            logger.error(
                "[FatSecret] API request failed",
                error=str(e),
                method=method,
                endpoint=endpoint,
                status_code=getattr(e.response, "status_code", None) if hasattr(e, "response") else None,
                response_text=getattr(e.response, "text", None) if hasattr(e, "response") else None,
            )
            raise FatSecretAPIError(f"API request failed: {str(e)}") from e

        except ValueError as e:
            logger.error("[FatSecret] Failed to parse JSON response", error=str(e), endpoint=endpoint)
            raise FatSecretAPIError("Failed to parse API response") from e

    def get_access_token(self) -> str:
        """Get or refresh the access token"""
        if self.access_token:
            return self.access_token

        try:
            logger.info("[FatSecret] Obtaining new access token")

            # Encode client credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {"grant_type": "client_credentials", "scope": "basic"}

            response = requests.post(self.BASE_URL, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]

            logger.info("[FatSecret] Successfully obtained access token")
            return self.access_token

        except (RequestException, ValueError, KeyError) as e:
            logger.error("[FatSecret] Failed to obtain access token", error=str(e), error_type=type(e).__name__)
            raise FatSecretAuthError(f"Failed to obtain access token: {str(e)}") from e

    def _ensure_auth(self) -> None:
        """Ensure we have a valid access token"""
        if not self.access_token:
            self.get_access_token()

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for foods in FatSecret database
        """
        try:
            logger.info(
                "[FatSecret] Searching database",
                query=query,
            )

            self._ensure_auth()

            data = self._make_request(
                method="GET", endpoint="foods/search/v1", params={"search_expression": query, "format": "json"}
            )

            # Handle empty or invalid responses
            if not data:
                logger.warning("[FatSecret] Empty response received", query=query)
                return []

            if "foods" not in data:
                logger.warning(
                    "[FatSecret] Missing 'foods' key in response",
                    query=query,
                    available_keys=list(data.keys()),
                    response_text=data,
                )
                return []

            foods_data = data["foods"]
            if "food" not in foods_data:
                logger.warning("[FatSecret] No food results found", query=query, response_text=data)
                return []

            results = foods_data["food"]
            logger.info("[FatSecret] Search completed successfully", query=query, results_count=len(results))
            return results

        except Exception as e:
            logger.error("[FatSecret] Search operation failed", error=str(e), error_type=type(e).__name__, query=query)
            raise

    def get_product_info(self, food_id: str) -> Dict[str, Any]:
        """
        Get detailed product information by food_id
        """
        try:
            logger.info("[FatSecret] Getting product details", food_id=food_id)

            self._ensure_auth()

            data = self._make_request(
                method="GET",
                endpoint="food/v4",
                params={"food_id": food_id, "include_food_images": "true", "format": "json"},
            )

            if not data or "food" not in data:
                logger.error(
                    "[FatSecret] Invalid product info response",
                    food_id=food_id,
                    response_keys=list(data.keys()) if data else None,
                )
                raise FatSecretAPIError(f"Invalid response for food_id: {food_id}")

            logger.info("[FatSecret] Successfully retrieved product details", food_id=food_id)
            return data["food"]

        except Exception as e:
            logger.error(
                "[FatSecret] Failed to get product details", error=str(e), error_type=type(e).__name__, food_id=food_id
            )
            raise
