from tests.conftest import client
from models import Conversation

def test_delete_conversation_success(authenticated_client, test_db):
    user = authenticated_client
    db = test_db

    response = user.delete(
        "/conversations/3"
    )

    assert response.status_code == 200

    assert response.json() == {
        "Message": "Conversation Deleted Successfully"
    }

    convo = db.query(Conversation).filter(Conversation.id == 3).first()

    assert convo is None

def test_delete_conversation_not_authenticated():

    response = client.delete(
            "/conversations/3"
        )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }

def test_delete_conversation_conversation_not_found(authenticated_client):
    user = authenticated_client

    response = user.delete(
        "/conversations/999",
    )

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "message": "User Doesnt have this Conversation"
    }

    