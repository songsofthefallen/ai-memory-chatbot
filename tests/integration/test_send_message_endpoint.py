from tests.conftest import client
from models import Message, Conversation
import uuid

def test_send_message_success(authenticated_client, test_db):
    user = authenticated_client
    db = test_db

    mess = f"test_content_{uuid.uuid4().hex[:8]}"

    response = user.post(
        "/conversations/5/messages",
        json={
            "content": mess
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "Message": "Message Sent Successfully"
    }

    message = db.query(Message).filter(Message.content == mess).first()

    convo = db.query(Conversation).filter(Conversation.id == 1).first()

    assert message is not None
    assert message.content == mess

    assert convo.latest_activity is not None

def test_send_message_not_authenticated():

    mess = f"test_content_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/conversations/1/messages",
        json={
            "content": mess
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }

def test_send_message_conversation_not_found(authenticated_client):
    user = authenticated_client

    mess = f"test_content_{uuid.uuid4().hex[:8]}"

    response = user.post(
        "/conversations/9999/messages",
        json={
            "content": mess
        }
    )

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "message": "User Doesnt have this Conversation"
    }

def test_send_message_invalid_request_body(authenticated_client):
    user = authenticated_client

    response = user.post(
        "/conversations/1/messages",
        json={}
    )

    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "content"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"


