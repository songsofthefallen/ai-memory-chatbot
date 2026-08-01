from tests.conftest import client

def test_login_success():

    response = client.post(
        "/login",
        data={
            "username": "Cas",
            "password": "12345678"

        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_cannot_find_user():

    response = client.post(
        "/login",
        data={
            "username": "test_user_not_exist",
            "password": "test_password"

        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "message": "User Not Found"
    }

    

def test_login_wrong_password():

    response = client.post(
            "/login",
            data={
                "username": "Cas",
                "password": "test_wrong_password"
    
            }
        )

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "message": "Incorrect Password"
    }

def test_login_missing_username():

    response = client.post(
            "/login",
            data={
                "password": "12345678"
    
            }
        )

    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "username"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"


def test_login_missing_password():

    response = client.post(
            "/login",
            data={
                "username": "Cas"
    
            }
        )

    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "password"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"

  