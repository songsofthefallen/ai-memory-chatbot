from tests.conftest import client, TestSessionLocal
from models import Message, Conversation
import uuid

def test_edit_message_success(authenticated_client, test_db):
    user = authenticated_client
    db = test_db

    new_mess = f"test_content_{uuid.uuid4().hex[:8]}"

    convo = db.query(Conversation).filter(Conversation.id == 1).first()

    old_time = convo.latest_activity

    response = user.put(
        "/conversations/1/messages/1",
        json={
            "content": new_mess
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "Message": "Message Updated Successfully"
    }
    fresh_db = TestSessionLocal() #get the new session to get new value not the value of old identity map

    convo = fresh_db.query(Conversation).filter(Conversation.id == 1).first()
    message = fresh_db.query(Message).filter(Message.id == 1).first()


    assert convo.latest_activity > old_time
    assert message.content == new_mess

    fresh_db.close()

def test_edit_message_not_authenticated():

    response = client.put(
            "/conversations/1/messages/1",
            json={
                "content": "new_message"
            }
        )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }


def test_edit_message_conversation_not_found(authenticated_client):
    user = authenticated_client

    response = user.put(
            "/conversations/9999/messages/1",
            json={
                "content": "new_message"
            }
        )
    
    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "message": "User Doesnt have this Conversation"
    }

def test_edit_message_message_not_found(authenticated_client):
    user = authenticated_client

    response = user.put(
            "/conversations/1/messages/9999",
            json={
                "content": "new_message"
            }
        )
    
    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "message": "Message Not Found"
    }


def test_edit_message_invalid_request_body(authenticated_client):
    user = authenticated_client

    response = user.put(
            "/conversations/1/messages/1",
            json={}
        )

    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "content"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"
