from tests.conftest import client, TestSessionLocal
from models import Message, Conversation

def test_search_messages_success(authenticated_client, test_db):
    user = authenticated_client
    db = test_db

    response = user.get(
        "/messages",
        params={
            "search": "test_content",
            "page": 1
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "test_content" in body[0]["content"]
    assert "conversation_id" in body[0]
    assert body[0]["role"] == "user"

def test_search_messages_not_authenticated():

    response = client.get(
        "/messages",
        params={
            "search": "test_content",
            "page": 1
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }

def test_search_messages_no_result_found(authenticated_client):
    user = authenticated_client

    response = user.get(
        "/messages",
        params={
            "search": "mess_does_not_exist",
            "page": 1
        }
    )

    assert response.status_code == 200

    assert response.json() == []

def test_search_messages_pagination_check(authenticated_client):
    user = authenticated_client

    response1 = user.get(
            "/messages",
            params={
                "search": "test_content",
                "page": 1
            }
        )
    
    response2 = user.get(
                "/messages",
                params={
                    "search": "test_content",
                    "page": 2
                }
            )

    body1 = response1.json()
    body2 = response2.json()

    assert len(body1) == 10

    assert body1 != body2

def test_search_messages_return_only_users_message(authenticated_client, test_db): #testing if another users doesnt messages doesnt get return
    user = authenticated_client
    db = test_db

    response1 = user.get(
        "/messages",
        params={
            "search": "test_content",
            "page": 1
        }
    )
    response2 = user.get(
            "/messages",
            params={
                "search": "test_content",
                "page": 2
            }
        )

    body1 = response1.json()
    body2 = response2.json()

    convo = db.query(Conversation).filter(Conversation.user_id == 6, Conversation.id == 1).first() #get convo where the id is the user(which is 6) and all the messages is stored in convo 1 thats all we needed

    assert convo is not None

    assert all(
        messages["conversation_id"] == convo.id
        for messages in body1
    )

    assert all(
            messages["conversation_id"] == convo.id
            for messages in body2
        )
    