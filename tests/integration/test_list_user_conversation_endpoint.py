from tests.conftest import client

def test_list_user_conversation_success(authenticated_client):
    user = authenticated_client

    response = user.get(
        "/conversations",
        params={
            "page": 1
        }
    )

    # print(response.status_code)
    # print(response.json())
        