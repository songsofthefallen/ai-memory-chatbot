from models import Conversation, Message
from fastapi import HTTPException

def find_convo_in_user(user, convo, db):
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    return conversation

def all_convo_in_user(user, page, db):
    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.latest_activity.desc()).offset(offset).limit(convo_per_page).all()
    if not conversation:
        raise HTTPException(status_code=404, detail='No Conversation Found')
    return conversation