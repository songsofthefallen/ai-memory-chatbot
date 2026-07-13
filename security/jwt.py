import os
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.getenv('JWT_KEY')

ALGORITHM = "HS256"

def get_token(user: int):

    expire = datetime.now(UTC) + timedelta(minutes=30)

    payload = {
        "sub": str(user.id), 
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def verify_token(token):
    try:
        payload = jwt.decode( #token is passed then 2 argument verify if same jwt_key using algo HS256
            token,
            JWT_KEY,
            algorithms=[ALGORITHM]
        )

        return payload
    except JWTError:
        return None