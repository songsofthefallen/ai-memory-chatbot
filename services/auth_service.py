from models import User, RefreshToken
from fastapi import HTTPException, Request, Depends
from database import get_db
from security.jwt import verify_access_token
import logging

logger = logging.getLogger(__name__)


def username_already_exist(name, db):
    user = db.query(User).filter(User.username == name).first()
    if user:
        logger.warning(
            "Registration failed: username '%s' already exists",
            name,
        )
        raise HTTPException(status_code=409, detail='Username already Exist')


def email_already_exist(email, db):
    user = db.query(User).filter(User.email == email).first()
    if user:
        logger.warning(
            "Registration failed: email '%s' already exists",
            email,
        )
        raise HTTPException(status_code=409, detail='Email already Exist')
  



def find_user(user, db):
    return db.query(User).filter(User.id == user).first()

def find_user_name(name, db):
    user = db.query(User).filter(User.username == name).first()
    if user is None:
        logger.warning(
            "User %s Not Found",
            name
        )
        raise HTTPException(status_code=404, detail='User Not Found')
    return user

def get_current_user(request: Request,  db = Depends(get_db)):
    token = request.cookies.get("access_token")

    if token is None:
        logger.warning("Not Authenticated")
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_access_token(token)

    username = payload["sub"]

    user = find_user(username, db)

    if user is None:
        logger.warning(
                    "User %s Not Found",
                    username
                )
        raise HTTPException(status_code=404, detail="User not Found")

    return user

def find_refresh_token(jti, db):
    find_token =  db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if find_token is None:
        logger.warning(
            "Token Not Found"
        )
        raise HTTPException(status_code=401, detail="Token Not Found")
    if find_token.revoked != False:
        logger.warning(
                    "Token Revoked"
                )
        raise HTTPException(status_code=401, detail="Token is Revoked")
    
    return find_token.token, find_token

def find_user_by_token(payload, db):
    username = payload["sub"]

    user = db.query(User).filter(User.id == username).first()
    if user is None:
        logger.warning(
            "User Not Found"
        )
        raise HTTPException(status_code=404, detail='User Not Found')
    return user