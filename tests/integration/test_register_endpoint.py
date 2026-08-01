from tests.conftest import client
import uuid

username = f"user_{uuid.uuid4().hex[:8]}"
email = f"email_{uuid.uuid4().hex[:8]}@gmail.com"


def test_register_success():

    response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": "12345678"
        }, 
    )

    assert response.status_code == 200

    assert response.json() == {
        "Message": "User Registered Successfully"
    }

def test_register_username_exist():

    response = client.post(
        "/register",
        json={
            "username": "username_exist",
            "email": "email_not_exist@test.com",
            "password": "12345678"
        }, 
    )

    
    assert response.status_code == 409

    assert response.json() == {
                "success": False,
                "message": "Username already Exist"
            }

    
    
def test_register_email_exist():

    response = client.post(
        "/register",
        json={
            "username": "username_not_exist",
            "email": "email_exist@test.com",
            "password": "12345678"
        }, 
    )

    
    assert response.status_code == 409
    
    assert response.json() == {
            "success": False,
            "message": "Email already Exist"
        }


def test_register_missing_username():

    response = client.post(
        "/register",
        json={
            "email": "test_email@test.com",
            "password": "12345678"
        }, 
    )

    
    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "username"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"


def test_register_missing_email():

    response = client.post(
        "/register",
        json={
            "username": "test_username",
            "password": "12345678"
        }, 
    )

    
    assert response.status_code == 422
    
    error = response.json()["detail"]
    
    assert error[0]["loc"] == ["body", "email"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"


def test_register_missing_password():

    response = client.post(
        "/register",
        json={
           "username": "test_username",
           "email": "test_email@test.com"
        }, 
    )

    
    assert response.status_code == 422
        
    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "password"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"

def test_register_invalid_email():

    response = client.post(
        "/register",
        json={
           "username": "test_username",
           "email": "not-valid-email",
           "password": "12345678"
        }, 
    )

    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["type"] == "value_error"
    assert error[0]["loc"] == ["body", "email"]







