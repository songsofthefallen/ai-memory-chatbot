from tests.conftest import client
from models import Conversation

def test_rename_conversation_success(authenticated_client, test_db):
    user = authenticated_client
    db = test_db

    response = user.put(
        "/conversations/1",
        json={
            "title": "fake_new_title"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "Message": "Title Renamed Successfully"
    }

    convo = db.query(Conversation).filter(Conversation.id == 1).first()

    assert convo.title == "fake_new_title"

def test_rename_conversation_not_authenticated():

    response = client.put(
        "/conversations/1",
        json={
            "title": "fake_new_title"
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }

def test_rename_conversation_conversation_not_found(authenticated_client):
    user = authenticated_client

    response = user.put(
        "/conversations/999",
        json={
            "title": "fake_new_title"
        }
    )

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "message": "User Doesnt have this Conversation"
    }

def test_rename_conversation_conversation_invalid_request_body(authenticated_client):
    user = authenticated_client

    response = user.put(
        "/conversations/999",
        json={}
    )

    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "title"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"


