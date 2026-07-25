import pytest
from models import User
from security.jwt import get_access_token, get_refresh_token, verify_access_token, verify_refresh_token
from jose import jwt
from fastapi import HTTPException
from config import settings
import hashlib
from datetime import timedelta

JWT_KEY = settings.JWT_KEY

ALGORITHM = "HS256"

def test_get_access_token():
    user = User(id=10, username="Luna")

    token = get_access_token(user)

    payload = jwt.decode(
        token,
        JWT_KEY,
        algorithms=[ALGORITHM]
    )

    assert payload["sub"] == "10"
    assert payload["type"] == "access"
    assert "exp" in payload

def test_get_refresh_token():
    user = User(id=10, username="Luna")
    
    hash_token ,token, _, jti = get_refresh_token(user)
    
    payload = jwt.decode(
        token,
        JWT_KEY,
        algorithms=[ALGORITHM]       
    )

    assert payload["sub"] == "10"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti
    assert "exp" in payload
    assert hash_token == hashlib.sha256(token.encode()).hexdigest()

def test_verify_access_token_valid():
    user = User(id=10, username="Luna")
    
    token = get_access_token(user)

    payload = verify_access_token(token)

    assert payload["sub"] == "10"
    assert payload["type"] == "access"

def test_verify_access_token_expired():
    user = User(id=10, username="Luna")
        
    token = get_access_token(user, expires_delta=timedelta(minutes=-1))

    with pytest.raises(HTTPException) as exc_info:
        verify_access_token(token)

    assert exc_info.value.detail == "Token expired"

def test_verify_access_token_invalid_type(): #generate refresh token instead of access
    user = User(id=10, username="Luna")
    
    _,token, _, _ = get_refresh_token(user)

    with pytest.raises(HTTPException) as exc_info:
        verify_access_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token Type"

def test_verify_access_token_invalid_signature(): 
    with pytest.raises(HTTPException)as exc_info:
        verify_access_token("abcdefg123")

    assert exc_info.value.detail == "Invalid token"

def test_verify_refresh_token_valid():
    user = User(id=10, username="Luna")
    
    hash_token, token, _, jti = get_refresh_token(user)

    payload = verify_refresh_token(token)

    assert payload["sub"] == "10"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti
    assert hash_token == hashlib.sha256(token.encode()).hexdigest()

def test_verify_refresh_token_expired():
    user = User(id=10, username="Luna")
        
    _,token, _, _ = get_refresh_token(user, expires_delta=timedelta(minutes=-1))

    with pytest.raises(HTTPException) as exc_info:
        verify_refresh_token(token)

    assert exc_info.value.detail == "Token expired"

def test_verify_refresh_token_invalid_type():
    user = User(id=10, username="Luna")
    
    token = get_access_token(user)

    with pytest.raises(HTTPException) as exc_info:
        verify_refresh_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token Type"

def test_verify_access_token_invalid_signature(): 
    with pytest.raises(HTTPException)as exc_info:
        verify_refresh_token("abcdefg123")

    assert exc_info.value.detail == "Invalid token"



    