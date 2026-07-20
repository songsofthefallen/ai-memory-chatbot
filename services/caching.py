from redis_client import redis
from services.message_service import return_all_messages
import json

def cache_aside(user, convo, page, db):

    key = f"user:{user.id}:conversation:{convo.id}:page:{page}"

    cache = redis.get(key)

    if cache:
        return cache.loads(cache) #if its json loads it before returning
    
    conversation = return_all_messages(user, convo, page, db)

    redis.set(key, json.dumps(conversation), ex=500) #if its nested data use json. dumps

    return conversation



