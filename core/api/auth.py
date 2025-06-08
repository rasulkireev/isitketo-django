from typing import Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest
from ninja.security import HttpBearer


class MultipleAuthSchema(HttpBearer):
    def authenticate(self, request: HttpRequest, token: Optional[str] = None) -> Optional[User]:
        if hasattr(request, "user") and request.user.is_authenticated:
            try:
                return request.user
            except User.DoesNotExist:
                return None

        # For API token authentication (when using the API directly)
        if token == settings.SECRET_API_TOKEN:
            return User.objects.get(id=1)

        return None

    def __call__(self, request):
        # Override to make authentication optional for session-based requests
        if hasattr(request, "user") and request.user.is_authenticated:
            return self.authenticate(request)

        return super().__call__(request)
