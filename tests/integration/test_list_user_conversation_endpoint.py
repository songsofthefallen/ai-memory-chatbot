from tests.conftest import client

def test_list_user_conversation_success(authenticated_client):
    user = authenticated_client

    response = user.get(
        "/conversations",
        params={
            "page": 1
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) > 0

def test_list_user_conversation_not_authenticated():

    response = client.get(
        "/conversations",
        params={
            "page": 1
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }

def test_list_user_conversation_not_conversation():

    client.post( #loggin in another user that has no conversation
        "/login",
        data={
            "username": "user_53e9dc79",
            "password": "12345678"
                }
    )

    response = client.get(
        "/conversations",
        params={
            "page": 1
        } 
    )
    assert response.status_code == 200

    body = response.json()

    assert body == []

def test_list_user_conversation_pagination_check(authenticated_client):
    user = authenticated_client

    response1 = user.get(
        "/conversations",
        params={
            "page": 1
        }
    )

    response2 = user.get(
        "/conversations",
        params={
            "page": 2
        }
    )

    body1 = response1.json()
    body2 = response2.json()

    assert len(body1) == 10

    assert body1 != body2
