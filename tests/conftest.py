import pytest
from unittest.mock import Mock
from services.caching import CacheService
from models import User

from fastapi.testclient import TestClient
from main import app
from database import get_db
from tests.integration.test_database import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def fake_database():
    fake_db = Mock()

    fake_user = User(id=1, username="Cas")

    return fake_db, fake_user


@pytest.fixture
def fake_cache():
    fake_redis = Mock()
    return CacheService(fake_redis), fake_redis

