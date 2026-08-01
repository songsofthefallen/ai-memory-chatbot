from tests.conftest import client
from security.jwt import get_access_token
from models import User

fake_user = User(id=1, username="fake_user")

def test_logout_success():
    access_token = get_access_token(fake_user)

    client.cookies.set( #settings it to delete it later
        "access_token",
        access_token
    )

    response = client.post("/logout")

    assert response.status_code == 200
    assert response.json() == {
        "Message": "Log out Success"
    }

    cookie = response.headers["set-cookie"]

    assert "access_token=" in cookie
    assert "Max-Age=0" in cookie
    assert "expires=" in cookie

def test_logout_fail():
    client.cookies.clear() #TestClient persists cookies across requests so deleting it for this to work

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }


