from models import Conversation, Message
from fastapi import HTTPException


def return_all_messages(user, convo, page, db):
    conversation =  db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo).first()

    if conversation is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    
    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    message = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.latest_activity.desc()).offset(offset).limit(convo_per_page).all()

    if not message:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")

    conversation.messages = message

    return conversation

def search_all_messages(user, search, page, db):
    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    messages = db.query(Message).join(Message.conversation).filter(Message.content.contains(search), Conversation.user_id == user.id).order_by(Message.create_at.desc()).offset(offset).limit(convo_per_page).all()
    if not messages:
        raise HTTPException(status_code=404, detail='No Message Found')
    return messages


def find_message(id, db):
    message = db.query(Message).filter(Message.id == id).first()
    if message is None:
        raise HTTPException(status_code=404, detail='Message Not Found!')
    return message
