import pytest
from fastapi import HTTPException
from services.auth_service import username_already_exist, email_already_exist, find_user, find_user_name, get_current_user, find_refresh_token, find_user_by_token
from models import User, RefreshToken
from unittest.mock import Mock, patch

def test_username_already_exist(fake_database):
    fake_db, fake_user = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = fake_user

    with pytest.raises(HTTPException)as exc_info:
        username_already_exist("Cas", fake_db)

    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == 'Username already Exist'


def test_username_not_exist(fake_database):
    fake_db, _ = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = None

    username_already_exist("Neph", fake_db)

    fake_db.query.assert_called_once_with(User)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()

def test_email_already_exist(fake_database):
    fake_db, fake_user = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = fake_user

    with pytest.raises(HTTPException)as exc_info:
        email_already_exist("fakeemai@gmail.com", fake_db)

    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == 'Email already Exist'

def test_email_not_exist(fake_database):
    fake_db, _ = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = None

    email_already_exist("fakeemai@gmail.com", fake_db)

    fake_db.query.assert_called_once_with(User)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()

def test_find_user(fake_database):
    fake_db, fake_user = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = fake_user

    result = find_user(1, fake_db)

    assert result == fake_user
    fake_db.query.assert_called_once_with(User)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()

def test_find_user_name_success(fake_database):
    fake_db, fake_user= fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = fake_user

    result = find_user_name("Cas", fake_db)

    assert result == fake_user
    fake_db.query.assert_called_once_with(User)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()


def test_find_user_name_fail(fake_database):
    fake_db, _ = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException)as exc_info:
        find_user_name("Cas", fake_db)

    exc_info.value.status_code == 404
    exc_info.value.detail == 'User Not Found'

def test_get_current_user_success(fake_database):    
    fake_db, fake_user = fake_database

    fake_request = Mock()

    fake_request.cookies.get.return_value = "token12345"# when someone calls cooke.get return this

    with patch("services.auth_service.verify_access_token") as verify, \
        patch("services.auth_service.find_user") as find:

        verify.return_value = {"sub": "Cas"}
        find.return_value = fake_user

        result = get_current_user(fake_request, fake_db)

        assert result == fake_user

        fake_request.cookies.get.assert_called_once_with("access_token") #means u did cookies.get("access_token")
        verify.assert_called_once_with("token12345")
        find.assert_called_once_with("Cas", fake_db)

def test_get_current_user_token_None(fake_database):
    fake_db, _ = fake_database
    fake_request = Mock()

    fake_request.cookies.get.return_value = None

    with pytest.raises(HTTPException)as exc_info:
        get_current_user(fake_request, fake_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"



def test_get_current_user_not_found(fake_database):
    fake_db, _ = fake_database
    fake_request = Mock()

    fake_request.cookies.get.return_value = "token12345"
    with patch("services.auth_service.verify_access_token") as verify, \
        patch("services.auth_service.find_user") as find:


        verify.return_value = {"sub": "Cas"}
        find.return_value = None

        with pytest.raises(HTTPException)as exc_info:
            get_current_user(fake_request, fake_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not Found"

def test_find_refresh_token_success(fake_database):
    fake_db, _ = fake_database

    fake_token = RefreshToken(
        jti="abcde",
        token="token12345",
        revoked=False
    )

    fake_db.query.return_value.filter.return_value.first.return_value = fake_token

    token, row = find_refresh_token("abcdef", fake_db)

    assert token == "token12345"
    assert row == fake_token
    fake_db.query.assert_called_once_with(RefreshToken)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()

def test_find_refresh_token_Not_Found(fake_database):
    fake_db, _ = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException)as exc_info:
        find_refresh_token("abcde", fake_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token Not Found"
    fake_db.query.assert_called_once_with(RefreshToken)

def test_find_refresh_token_revoked(fake_database):
    fake_db, _ = fake_database

    fake_token = RefreshToken(
            jti="abcde",
            token="token12345",
            revoked=True
        )
    
    fake_db.query.return_value.filter.return_value.first.return_value = fake_token
    
    with pytest.raises(HTTPException)as exc_info:
        find_refresh_token("abcde", fake_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token is Revoked"
    fake_db.query.assert_called_once_with(RefreshToken)

def test_find_user_by_token_success(fake_database):
    fake_db, _ = fake_database

    fake_user = User(
        username="Cas"
    )

    token = {
    "sub": "Cas"
    }

    fake_db.query.return_value.filter.return_value.first.return_value = fake_user

    result = find_user_by_token(token, fake_db)

    assert result == fake_user
    fake_db.query.assert_called_once_with(User)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()

def test_find_user_by_token_failed(fake_database):
    fake_db, _ = fake_database

    token = {
            "sub": "Cas"
        }

    fake_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException)as exc_info:
        find_user_by_token(token, fake_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'User Not Found'
    fake_db.query.assert_called_once_with(User)
    



    













        














    

