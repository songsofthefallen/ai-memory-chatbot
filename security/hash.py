import bcrypt
from fastapi import HTTPException
import hashlib

def hash_password(password):
    hashed_pass = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")
    
    return hashed_pass

def decode_hash(form_password, user_password):
    if not bcrypt.checkpw(
        form_password.encode("utf-8"),
        user_password.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Incorrect Password")
    


def decode_hash_token(token, hashed_token):
    hashing_token = hashlib.sha256(token.encode()).hexdigest()

    if hashing_token != hashed_token:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
