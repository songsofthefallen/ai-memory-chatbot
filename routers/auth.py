from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from schemas import RegisterUser
from database import get_db
from models import User, RefreshToken
from services.auth_service import find_refresh_token, find_user_by_token, find_user_name, username_already_exist, email_already_exist, get_current_user
from security.jwt import get_access_token, get_refresh_token, verify_refresh_token
from security.hash import hash_password, decode_hash, decode_hash_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/register')
def register_user(user: RegisterUser, db = Depends(get_db)):

    username_already_exist(user.username, db)

    email_already_exist(user.email, db)
    
    hashed_pass = hash_password(user.password)

    db_user = User(username = user.username, email = user.email, hashed_password = hashed_pass)

    db.add(db_user)
    db.commit()

    logger.info(
            "User '%s' registered successfully",
            user.username,
        )


    return {
       "Message": "User Registered Successfully"
   }

@router.post('/login') 
def login_user(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)): #oauth expect from data not json so no pydantic model

    stored_user = find_user_name(form_data.username, db)
    
    decode_hash(form_data.password, stored_user.hashed_password)

    access_token = get_access_token(stored_user)

    hashed_rt, refresh_token, expire, jti = get_refresh_token(stored_user) #hashed

    db_rt = RefreshToken(token = hashed_rt, jti = jti, user_id = stored_user.id, expires_at = expire)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age =  60 * 60 * 24 * 30
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age =  900
    )

    db.add(db_rt)
    db.commit()

    logger.info(
        "User '%s' authenticated successfully",
        form_data.username,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post('/refresh')
def refresh_token(token: str, db = Depends(get_db)):
    
    verified_token = verify_refresh_token(token) #verify the authenticity of token also get the jti

    jti = verified_token["jti"]

    hashed_token, row = find_refresh_token(jti, db) #find refresh token in database also get the row to know which token to change

    decode_hash_token(token, hashed_token) #verify if the token passed and the hashed token in database is the same

    user = find_user_by_token(verified_token, db)

    new_access_token = get_access_token(user)

    hashed_new_rf_token, new_refresh_token, _ , jti = get_refresh_token(user)

    row.token = hashed_new_rf_token
    row.jti = jti

    db.commit()

    logger.info(
            "User '%s' Token Refreshed",
            user.username,
        )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
    
@router.post('/logout')
def logout(response: Response, current_user: User = Depends(get_current_user)): #get the current user im not using the variable
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    logger.info(
    "Access token revoked for user '%s'",
    current_user.username,
)

    return {
        "Message": "Log out Success"
    }


