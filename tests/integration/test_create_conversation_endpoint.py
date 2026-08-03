from tests.conftest import client
from models import Conversation
import uuid

title = f"test_title_{uuid.uuid4().hex[:8]}"

def test_create_conversation_success(authenticated_client, test_db):
    user = authenticated_client 
    db = test_db

    title = f"test_title_{uuid.uuid4().hex[:8]}"

    response = user.post(
        "/conversations",
        json={
            "title": title
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "Message": "Conversation Created Successfully"
    }
    convo = db.query(Conversation).filter_by(title=title).first()

    assert convo is not None
    assert convo.title == title
    
def test_create_conversation_not_authenticated():
    title = f"test_title_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/conversations",
        json={
            "title": title
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "message": "Not authenticated"
    }

def test_create_conversation_invalid_request_body(authenticated_client):
    user = authenticated_client

    response = user.post(
        "/conversations",
        json={}
    )

    assert response.status_code == 422

    error = response.json()["detail"]

    assert error[0]["loc"] == ["body", "title"]
    assert error[0]["msg"] == "Field required"
    assert error[0]["type"] == "missing"

