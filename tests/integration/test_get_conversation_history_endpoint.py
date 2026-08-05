from tests.conftest import client

def test_get_conversation_history_success(authenticated_client):
    user = authenticated_client

    response = user.get(
        "/conversation/1",
        params={
            "page:": 1
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert "messages" in body

def test_get_conversation_history_not_authenticated():

    response = client.get(
        "/conversation/1",
        params={
            "page:": 1
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }


def test_get_conversation_history_not_found(authenticated_client):
    user = authenticated_client

    response = user.get(
        "/conversation/999",
        params={
            "page:": 1
        }
    )
    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "message": "User Doesnt have this Conversation"
    }


def test_get_conversation_history_no_message(authenticated_client):
    user = authenticated_client

    response = user.get(
        "/conversation/15", #this conversation 15 does not contain any messages
        params={
            "page:": 1
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 15
    assert body["messages"] == []

def test_get_conversation_history_pagination_check(authenticated_client):
    user = authenticated_client

    response1 = user.get(
        "/conversation/1",
        params={
            "page": 1
        }
    )

    response2 = user.get(
        "/conversation/1",
        params={
            "page": 2
        }
    )

    body1 = response1.json()
    body2 = response2.json()

    assert len(body1["messages"]) == 10

    assert body1 != body2
