import secrets
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ninja.security import HttpBearer


class MultipleAuthSchema(HttpBearer):
    def authenticate(self, request: HttpRequest, token: Optional[str] = None):
        if hasattr(request, "user") and request.user.is_authenticated:
            try:
                return request.user
            except get_user_model().DoesNotExist:
                return None

        # For API token authentication (when using the API directly)
        if secrets.compare_digest(token or "", settings.SECRET_API_TOKEN):
            return get_user_model().objects.filter(is_superuser=True).first()

        return None

    def __call__(self, request):
        # Override to make authentication optional for session-based requests
        if hasattr(request, "user") and request.user.is_authenticated:
            return self.authenticate(request)

        return super().__call__(request)
