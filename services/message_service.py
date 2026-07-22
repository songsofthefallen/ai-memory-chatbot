from models import Conversation, Message
from fastapi import HTTPException
from services.conversation_service import find_convo_in_user
from datetime import datetime, UTC
from schemas import ConversationResponse, MessagesResponse
from services.caching import CacheService, CacheKeys

def find_message(id, convo_id, db):
    message = db.query(Message).filter(Message.conversation_id== convo_id, Message.id == id).first()
    if message is None:
        raise HTTPException(status_code=404, detail='Message Not Found!')
    return message

def send_message(convo_id, message, current_user, db):
    conversation = find_convo_in_user(current_user, convo_id, db)

    db_message = Message(conversation_id = convo_id, role = "user", content = message.content)

    conversation.latest_activity = datetime.now(UTC)

    db.add(db_message)
    db.commit()

    CacheService.invalidate_cache_message(current_user.id, convo_id)
    CacheService.invalidate_cache_search(current_user.id)
    

def edit_message(convo_id, mess_id, new_message, current_user, db):
    conversation = find_convo_in_user(current_user, convo_id, db)

    message = find_message(mess_id, conversation.id, db)
    
    message.content = new_message.content
    conversation.latest_activity = datetime.now(UTC)

    db.commit()

    CacheService.invalidate_cache_message(current_user.id, convo_id)
    CacheService.invalidate_cache_search(current_user.id)

def search_all_messages(user, search, page, db):
    key = CacheKeys.search_message(user, search, page)

    cache = CacheService.get_cache(key)

    if cache:
        return cache
    

    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    messages = db.query(Message).join(Message.conversation).filter(Message.content.contains(search), Conversation.user_id == user.id).order_by(Message.create_at.desc()).offset(offset).limit(convo_per_page).all()
    if not messages:
        raise HTTPException(status_code=404, detail='No Message Found')
    
    message_dict = [MessagesResponse.model_validate(mess).model_dump() for mess in messages]

    CacheService.set_cache(key, message_dict)

    return messages

def return_all_messages(user, convo_id, page, db):

    key = CacheKeys.all_messages(user, convo_id, page)

    cache = CacheService.get_cache(key)

    if cache:
        return cache
    
    conversation =  db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo_id).first()

    if conversation is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    
    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.latest_activity.desc()).offset(offset).limit(convo_per_page).all()

    conversation.messages = messages

    conversation_dict = ConversationResponse.model_validate(conversation).model_dump()

    CacheService.set_cache(key, conversation_dict)

    return conversation

