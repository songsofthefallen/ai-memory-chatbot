from redis_client import redis
from services.message_service import return_all_messages
from services.conversation_service import  all_convo_in_user
import json
from schemas import ConversationsResponse, ConversationResponse

def all_messages_cache(user, convo_id, page, db):

    key = f"user:{user.id}:conversation:{convo_id}:messages:page:{page}"

    cache = redis.get(key)

    if cache:
        return json.loads(cache) #if its json loads it before returning
    
    conversation = return_all_messages(user, convo_id, page, db)

    conversation_dict = ConversationResponse.model_validate(conversation).model_dump()

    redis.set(key, json.dumps(conversation_dict), ex=500) #if its nested data use json. dumps

    return conversation_dict


def all_convo_cache(user, page, db):
    key = f"user:{user.id}:conversations:page:{page}"

    cache = redis.get(key)

    if cache:
        return json.loads(cache) #if its json loads it before returning
    
    conversations = all_convo_in_user(user, page, db)

    conversation_dict = [ConversationsResponse.model_validate(convo).model_dump()for convo in conversations] #turn python object into something json can understand its a list of convo so loop 

    redis.set(key, json.dumps(conversation_dict), ex=500) #if its nested data use json. dumps

    return conversation_dict

def invalidate_cache(pattern):
    keys = redis.keys(pattern)

    if keys:
        redis.delete(*keys)