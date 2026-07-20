import os
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
from fastapi import HTTPException
import secrets
import hashlib

load_dotenv()

JWT_KEY = os.getenv('JWT_KEY')

ALGORITHM = "HS256"

def get_access_token(user):

    expire = datetime.now(UTC) + timedelta(minutes=10)

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

    return token


    

def get_refresh_token(user):

    expire = datetime.now(UTC) + timedelta(days=30)

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

    return hashed_token, token, expire, jti
  
 

def verify_access_token(token):
    try:
        payload = jwt.decode( #token is passed then 2 argument verify if same jwt_key using algo HS256
            token,
            JWT_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        if payload.get("sub") is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    


def verify_refresh_token(token):
    try:
        payload = jwt.decode(
            token,
            JWT_KEY,
            algorithms=ALGORITHM
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        if payload.get("sub") is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        if payload.get("jti") is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

