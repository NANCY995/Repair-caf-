import os
import pytest
from fastapi.testclient import TestClient

os.environ["APP_ENV"] = "testing"
os.environ["ADMIN_API_TOKEN"] = "test-admin-token"
os.environ["WHATSAPP_APP_SECRET"] = "test-app-secret"
os.environ["WHATSAPP_VERIFY_TOKEN"] = "test-verify"

from config import get_settings
get_settings.cache_clear()

from app import app as _app


@pytest.fixture
def client():
    return TestClient(_app)


@pytest.fixture
def admin_headers():
    return {"X-Admin-Token": "test-admin-token"}
