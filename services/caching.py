from redis_client import redis
import json

class CacheService:

    @staticmethod
    def get_cache(key):
        value = redis.get(key)

        if value:
            return json.loads(value)
        
        return None

    @staticmethod
    def set_cache(key, value, exp=800):
        redis.set(key, json.dumps(value), ex=exp)
        
    @staticmethod
    def invalidate_cache_conversation(user_id):
        keys = redis.keys(f"user:{user_id}:conversations:page:*")

        if keys:
            redis.delete(*keys)

    @staticmethod
    def invalidate_cache_message(user_id, convo_id):
        keys = redis.keys(f"user:{user_id}:conversation:{convo_id}:messages:page:*")

        if keys:
            redis.delete(*keys)

    @staticmethod
    def invalidate_cache_search(user_id):
        keys = redis.keys(f"user:{user_id}:search:*")

        if keys:
            redis.delete(*keys)

    

        

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


