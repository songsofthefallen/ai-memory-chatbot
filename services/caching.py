import json
from config import settings

class CacheService:
    def __init__(self, client):
        self.redis = client

    def get_cache(self, key):
        value = self.redis.get(key)

        if value:
            return json.loads(value)
        
        return None

    def set_cache(self, key, value):
        self.redis.set(key, json.dumps(value), ex=settings.CACHE_TTL)
        
    def invalidate_cache_conversation(self, user_id):
        keys = self.redis.keys(f"user:{user_id}:conversations:page:*")

        if keys:
            self.redis.delete(*keys)

    def invalidate_cache_message(self, user_id, convo_id):
        keys = self.redis.keys(f"user:{user_id}:conversation:{convo_id}:messages:page:*")

        if keys:
            self.redis.delete(*keys)

    def invalidate_cache_search(self, user_id):
        keys = self.redis.keys(f"user:{user_id}:search:*")

        if keys:
            self.redis.delete(*keys)

    

class CacheKeys:
    @staticmethod
    def all_conversation(user, page):
        return f"user:{user.id}:conversations:page:{page}"
    
    @staticmethod
    def search_message(user, search, page):
        return f"user:{user.id}:search:{search}:page:{page}"
    
    @staticmethod
    def all_messages(user, convo_id, page):
        return f"user:{user.id}:conversation:{convo_id}:messages:page:{page}"


