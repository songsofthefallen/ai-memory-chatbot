from models import User, Conversation, RefreshToken, Message
from security.jwt import verify_access_token
from fastapi import HTTPException
from sqlalchemy.orm import joinedload


def find_user(user, db):
    return db.query(User).filter(User.id == user).first()

def find_user_name(name, db):
    return db.query(User).filter(User.username == name).first()

def find_convo(convo, db):
    return db.query(Conversation).filter(Conversation.id == convo).first()

def get_current_user(token, db):
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(status_code=400, detail="Invalid Token")
    
    username = payload["sub"]

    user = find_user(username, db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not Found")

    return user

def find_convo_in_user(user, convo, db):
    return db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo).first()

def return_all_messages(user, convo, page, db):
    conversation =  db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo).first()

    if conversation is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")

    message = db.query(Message).filter(Message.conversation_id == conversation.id).offset((page - 1) * 10).limit(10).all()

    conversation.messages = message


    return conversation


def all_convo_in_user(user, page, db):
    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    return db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.create_at).offset(offset).limit(convo_per_page).all()

def find_refresh_token(token, db):
    find_token =  db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if find_token is None:
        raise HTTPException(status_code=401, detail="Token Not Found")
    if find_token.revoked != False:
        raise HTTPException(status_code=401, detail="Token is Revoked")
    
    return find_token.token, find_token

def find_user_by_token(token, db):
    return db.query(User).filter(User.id == token["sub"]).first()

def get_all_messages(user, search, page, db):
    convo_per_page = 10
    offset = (page - 1) * convo_per_page
    return db.query(Message).join(Message.conversation).filter(Message.content.contains(search), Conversation.user_id == user.id).order_by(Message.create_at).offset(offset).limit(convo_per_page).all()

def find_message(id, db):
    return db.query(Message).filter(Message.id == id).first()


    


