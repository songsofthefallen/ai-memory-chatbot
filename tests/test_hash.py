import pytest
from fastapi import HTTPException
from security.hash import hash_password, decode_hash, decode_hash_token
import hashlib

def test_hash_password():
    hashed = hash_password("clownpassword")

    assert hashed != "clownpassword"

def test_decode_hash_valid_password():
    password = "clownpassword"
    hashed = hash_password(password)

    decode_hash(password, hashed)

def test_decode_hash_invalid_password():
    hashed = hash_password("clownpassword")
    with pytest.raises(HTTPException) as exc_info:
        decode_hash("wrongpassword", hashed)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect Password"

def test_decode_hash_token_valid():
    token = "abc123"
    hashed = hashlib.sha256(token.encode()).hexdigest()

    decode_hash_token(token, hashed)


def test_decode_hash_token_invalid():
    token = "abc123"
    hashed = hashlib.sha256(token.encode()).hexdigest()
    with pytest.raises(HTTPException) as exc_info:
        decode_hash_token("wrongpasswordtoken", hashed)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"
