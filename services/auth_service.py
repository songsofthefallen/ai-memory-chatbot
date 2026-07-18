from models import RefreshToken, User
from fastapi import HTTPException, Depends
from security.jwt import verify_access_token
from database import get_db
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") #login endpoint passed in get_current_user jwt dependency

def username_already_exist(name, db):
    user = db.query(User).filter(User.username == name).first()
    if user:
        raise HTTPException(status_code=409, detail='Username already Exist')
    return name

def email_already_exist(email, db):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=409, detail='Email already Exist')
    return email



def find_user(user, db):
    return db.query(User).filter(User.id == user).first()

def find_user_name(name, db):
    user = db.query(User).filter(User.username == name).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User NOt Found')
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(status_code=400, detail="Invalid Token")
    
    username = payload["sub"]

    user = find_user(username, db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not Found")

    return user

def find_refresh_token(token, db):
    find_token =  db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if find_token is None:
        raise HTTPException(status_code=401, detail="Token Not Found")
    if find_token.revoked != False:
        raise HTTPException(status_code=401, detail="Token is Revoked")
    
    return find_token.token, find_token

def find_user_by_token(token, db):
    user = db.query(User).filter(User.id == token["sub"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User Not Found')
    return user