from models import User, Conversation
from security.jwt import verify_token
from fastapi import HTTPException



def find_user(user, db):
    return db.query(User).filter(User.id == user).first()

def find_user_name(name, db):
    return db.query(User).filter(User.username == name).first()

def find_convo(convo, db):
    return db.query(Conversation).filter(Conversation.id == convo).first()

def get_current_user(token, db):
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(status_code=400, detail="Invalid Token")
    
    username = payload["sub"]

    user = find_user(username, db)

    return user

