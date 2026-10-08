"""Isolated local/CI settings; never use external credentials or services."""

import os

for name in (
    "SECRET_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "FAT_SECRET_CLIENT_ID",
    "FAT_SECRET_CLIENT_SECRET",
    "ANTHROPIC_API_KEY",
    "REPLICATE_API_KEY",
    "BUTTONDOWN_API_TOKEN",
    "SECRET_API_TOKEN",
):
    os.environ[name] = "test-only-not-a-credential"
os.environ.update(
    {
        "ENVIRONMENT": "test",
        "DEBUG": "False",
        "ALLOWED_HOSTS": "testserver,localhost,example.com",
        "CSRF_TRUSTED_ORIGINS": "https://example.com",
        "DATABASE_URL": "sqlite://:memory:",
        "AWS_S3_ENDPOINT_URL": "https://storage.example.com",
        "REDIS_URL": "redis://localhost:6379/15",
        "SENTRY_DSN": "",
        "LOGFIRE_TOKEN": "",
    }
)
from isitketo.settings import *  # noqa: E402,F403

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
STATICFILES_DIRS = []
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
