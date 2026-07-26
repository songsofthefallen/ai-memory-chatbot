from services.caching import CacheKeys
import json
from config import settings
from models import User





def test_get_cache_hit(fake_cache):
    f_cache, fake_redis = fake_cache
    fake_redis.get.return_value = '{"name":"Cas"}' #whatever the key return this

    result = f_cache.get_cache("user:1")

    assert result == {"name":"Cas"}
    fake_redis.get.assert_called_once_with("user:1") 


def test_get_cache_miss(fake_cache):
    f_cache, fake_redis = fake_cache
    fake_redis.get.return_value = None

    result = f_cache.get_cache("user:1")

    assert result is None 

def test_set_cache(fake_cache):
    f_cache, fake_redis = fake_cache
    f_cache.set_cache(
        "user:1",
        {"name":"John"}
        )

    fake_redis.set.assert_called_once_with(
        "user:1",
        json.dumps({"name": "John"}),
        ex=settings.CACHE_TTL
    )

def test_invalidate_cache_conversation_key_existed(fake_cache): #keys existed scenario
    f_cache, fake_redis = fake_cache
    fake_redis.keys.return_value = [ #whatever redis.key is return this
        "user:1:conversations:page:1",
        "user:1:conversations:page:2"
    ]

    f_cache.invalidate_cache_conversation(1) 

    fake_redis.delete.assert_called_once_with( #compares it here and the one inside function
        "user:1:conversations:page:1",
        "user:1:conversations:page:2"
    )

def test_invalidate_cache_conversation_no_key_existed(fake_cache):
    f_cache, fake_redis = fake_cache
    fake_redis.keys.return_value = []

    f_cache.invalidate_cache_conversation(1) 

    fake_redis.delete.assert_not_called()

def test_invalidate_cache_message_key_existed(fake_cache):
    f_cache, fake_redis = fake_cache
    fake_redis.keys.return_value = [ 
        "user:1:conversations:conversation:1:messages:page:1",
        "user:1:conversations:conversation:1:messages:page:2"
    ]

    f_cache.invalidate_cache_message(1, 1) 

    fake_redis.delete.assert_called_once_with( 
        "user:1:conversations:conversation:1:messages:page:1",
        "user:1:conversations:conversation:1:messages:page:2"
    )

def test_invalidate_cache_message_not_key_existed(fake_cache):
    f_cache, fake_redis = fake_cache
    fake_redis.keys.return_value = []

    f_cache.invalidate_cache_message(1, 1) 

    fake_redis.delete.assert_not_called()

def test_invalidate_cache_search_key_existed(fake_cache):
    f_cache, fake_redis = fake_cache
    fake_redis.keys.return_value = [ 
        "user:1:search:test1",
        "user:1:searh:test2"
    ]

    f_cache.invalidate_cache_search(1) 

    fake_redis.delete.assert_called_once_with( 
        "user:1:search:test1",
        "user:1:searh:test2"
    )

def test_invalidate_cache_search_not_key_existed(fake_cache):
    f_cache, fake_redis = fake_cache
    fake_redis.keys.return_value = []

    f_cache.invalidate_cache_search(1) 

    fake_redis.delete.assert_not_called()

def test_all_conversation():
    user = User(id=1)

    result = CacheKeys.all_conversation(user, 1)

    assert result == "user:1:conversations:page:1"

def test_search_message():
    user = User(id=1)

    result = CacheKeys.search_message(user, "test", 1)

    assert result == "user:1:search:test:page:1"

def test_all_messages():
    user = User(id=1)
    
    result = CacheKeys.all_messages(user, 1, 1)    

    assert result == "user:1:conversation:1:messages:page:1"


