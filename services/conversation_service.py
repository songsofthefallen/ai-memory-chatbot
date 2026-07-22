from models import Conversation
from fastapi import HTTPException
from services.caching import CacheService, CacheKeys
from schemas import ConversationsResponse
from datetime import datetime, UTC

def create_conversation(convo, current_user, db):
    db_convo = Conversation(title = convo.title, user_id = current_user.id, latest_activity = datetime.now(UTC))

    db.add(db_convo)
    db.commit()

    CacheService.invalidate_cache_conversation(current_user.id)


def rename_conversation(convo_id, new_title, current_user, db):
    convo_in_user = find_convo_in_user(current_user, convo_id, db)
    
    convo_in_user.title = new_title.title

    db.commit()

    CacheService.invalidate_cache_conversation(current_user.id)


def delete_conversation(convo_id, current_user, db):
    conversation = find_convo_in_user(current_user, convo_id, db)

    db.delete(conversation)
    db.commit()

    CacheService.invalidate_cache_conversation(current_user.id)


def find_convo_in_user(user, convo, db):
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    return conversation

def all_convo_in_user(user, page, db):
    key = CacheKeys.all_conversation(user, page)

    cache = CacheService.get_cache(key)

    if cache:
        return cache
    
    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    conversations = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.latest_activity.desc()).offset(offset).limit(convo_per_page).all()
   
    conversation_dict = [ConversationsResponse.model_validate(convo).model_dump()for convo in conversations] #turn python object into something json can understand its a list of convo so loop 

    CacheService.set_cache(key, conversation_dict)

    return conversations