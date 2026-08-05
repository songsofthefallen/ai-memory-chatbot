import pytest
from unittest.mock import Mock
from services.caching import CacheService
from models import User

from fastapi.testclient import TestClient
from main import app
from database import get_db
from tests.integration.test_database import override_get_db, TestSessionLocal

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

@pytest.fixture
def authenticated_client():

    client = TestClient(app)

    client.post(
        "/login",
        data={
            "username": "Cas",
            "password": "12345678"
        }
    ) 

    return client

@pytest.fixture
def test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

