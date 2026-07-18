import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas import RegisterUser
from database import get_db
from models import User, RefreshToken
from logger import logger
from services.auth_service import find_refresh_token, find_user_by_token, find_user_name, username_already_exist, email_already_exist
from security.jwt import get_access_token, get_refresh_token, verify_refresh_token
from security.hash import hash_password, decode_hash




router = APIRouter()


@router.post('/register')
def register_user(user: RegisterUser, db = Depends(get_db)):

    username_already_exist(user.username, db)

    email_already_exist(user.email, db)
    
    hashed_pass = hash_password(user.password)

    db_user = User(username = user.username, email = user.email, hashed_password = hashed_pass)

    db.add(db_user)
    db.commit()

    logger.info("User Registered Successfully")

    return {
       "Message": "User Registered Successfully"
   }

@router.post('/login') 
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)): #oauth expect from data not json so no pydantic model

    stored_user = find_user_name(form_data.username, db)
    
    decode_hash(form_data.password, stored_user.hashed_password)

    access_token = get_access_token(stored_user)

    refresh_token, expire = get_refresh_token(stored_user)

    db_rt = RefreshToken(token = refresh_token, user_id = stored_user.id, expires_at = expire)

    db.add(db_rt)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post('/refresh')
def refresh_token(token: str, db = Depends(get_db)):
    exist_token, row = find_refresh_token(token, db)

    if not exist_token:
        raise HTTPException(status_code=404, details='Token Not Found')
    
    verified_token = verify_refresh_token(exist_token)

    if verified_token is None:
        raise HTTPException(status_code=404, detail='Token Not Found')

    user = find_user_by_token(verified_token, db)

    new_access_token = get_access_token(user)

    new_refresh_token, _ = get_refresh_token(user)

    row.token = new_refresh_token

    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
    
