from tests.conftest import client
from models import User

fake_user = User(id=1, username="fake_user")

def test_logout_success(authenticated_client):
    user = authenticated_client

    response = user.post("/logout")

    assert response.status_code == 200
    assert response.json() == {
        "Message": "Log out Success"
    }

    cookie = response.headers["set-cookie"]

    assert "access_token=" in cookie
    assert "Max-Age=0" in cookie
    assert "expires=" in cookie

def test_logout_fail():

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }


