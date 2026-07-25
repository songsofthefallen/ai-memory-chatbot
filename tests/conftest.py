import pytest
from unittest.mock import Mock
from services.caching import CacheService
from models import User

@pytest.fixture
def fake_database():
    fake_db = Mock()

    fake_user = User(id=1, username="Cas")

    return fake_db, fake_user


@pytest.fixture
def fake_cache():
    fake_redis = Mock()
    return CacheService(fake_redis), fake_redis
 