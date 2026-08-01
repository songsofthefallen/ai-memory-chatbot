from config import settings
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException
import secrets
import hashlib
import logging

logger = logging.getLogger(__name__)

JWT_KEY = settings.JWT_KEY

ALGORITHM = "HS256"

def get_access_token(user, expires_delta: timedelta | None = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=10)

    expire = datetime.now(UTC) + expires_delta

    payload = {
        "sub": str(user.id),
        "type": "access", 
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_KEY,
        algorithm=ALGORITHM
    )

    logger.info(
            "User %s Got Access Token",
            user.username,
        )

    return token


    

def get_refresh_token(user, expires_delta: timedelta | None = None):
    if expires_delta is None:
        expires_delta = timedelta(days=30)

    expire = datetime.now(UTC) + expires_delta

    jti = secrets.token_hex(16)

    payload = {
        "sub": str(user.id),
        "type": "refresh", 
        "jti": jti,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_KEY,
        algorithm=ALGORITHM
    )

    hashed_token = hashlib.sha256(token.encode()).hexdigest()

    logger.info(
        "User %s Got Refresh Token",
        user.username,
    )

    return hashed_token, token, expire, jti
  
 

def verify_access_token(token):
    try:
        payload = jwt.decode( #token is passed then 2 argument verify if same jwt_key using algo HS256
            token,
            JWT_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            logger.warning(
                "Invalid Token Type"
            )
            raise HTTPException(status_code=401, detail="Invalid Token Type")

        if payload.get("sub") is None:
            logger.warning(
                "Invalid Token"
            )
            raise HTTPException(status_code=401, detail="Invalid token")

        return payload
    
    except ExpiredSignatureError:
        logger.exception(
            "Token Expired"
        )
        raise HTTPException(status_code=401, detail="Token expired")

    except JWTError:
        logger.exception(
            "Invalid Token"
        )
        raise HTTPException(status_code=401, detail="Invalid token")
    


def verify_refresh_token(token):
    try:
        payload = jwt.decode(
            token,
            JWT_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid Token Type")

        if payload.get("sub") is None:
            logger.warning(
                "Invalid Token"
            )
            raise HTTPException(status_code=401, detail="Invalid token")
        
        if payload.get("jti") is None:
            logger.warning(
                "Invalid Token"
            )
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return payload
    
    except ExpiredSignatureError:
        logger.exception(
            "Token Expired"
        )
        raise HTTPException(status_code=401, detail="Token expired")

    except JWTError:
        logger.exception(
            "Invalid Token"
        )
        raise HTTPException(status_code=401, detail="Invalid token")

