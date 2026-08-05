from tests.conftest import client

def test_refresh_token_success(): # works once cause the refresh token wil be change too so it will be invalid after refreshing once

    response = client.post(
        "/refresh",
        params={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidHlwZSI6InJlZnJlc2giLCJqdGkiOiI0MzUzOGEwNGE1OTFiZTc4OTY0ZDExN2Q3MTg3Nzk0MCIsImV4cCI6MTc4ODE4MjYyMX0.xbEwBxhgd2YsOm2AZxZ5S8vFN0swovbRwQRuDZvuL2Q" #its from test database so using it wont work. just for test
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"

def test_refreh_token_expired():

    response = client.post(
        "/refresh",
        params={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidHlwZSI6InJlZnJlc2giLCJqdGkiOiIzY2JjMmZhYmIwNTc0YTVkNjZhMGVmOGE0M2QwNjRjNCIsImV4cCI6MTc4NTU3NDgwNn0.PEuJODFtVZjX5scUKxOqIp4o0HS7xExY51VhYRoPAUM" #its from test database so using it wont work. just for test
        }
    )

    assert response.status_code == 401

    assert response.json() == {
            "success": False,
            "message": "Token expired"
        }
    


def test_refreh_token_invalid_jwt_format():

    response = client.post(
        "/refresh",
        params={
            "token": "invalid_jwt_format" 
        }
    )

    assert response.status_code == 401

    assert response.json() == {
            "success": False,
            "message": "Invalid token"
        }


def test_refreh_token_wrong_token_type(): #passed an access_token instead of refresh access token will expired in 10 minutes so it will change to signature expired if times up

    response = client.post(
        "/refresh",
        params={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MTc4NTU5MTIyMX0.JH2NTUMIrKPf69Hm0uVB93SElt1PvcaB1kr7mCiSn28" #its from test database so using it wont work. just for test
        }
    )

    assert response.status_code == 401

    assert response.json() == {
            "success": False,
            "message": "Invalid Token Type"
    }

def test_refreh_token_not_found():

    response = client.post(
        "/refresh",
        params={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidHlwZSI6InJlZnJlc2giLCJqdGkiOiJhMmZhMzdjNTVkYmUyY2FjMTZjMWQ4ZmExMDNiYjI2ZiIsImV4cCI6MTc4ODE2ODMzOH0.V1L6O-sQX5Mb82ilDfzrJ3jV-zaj7LyKepUhuwxUXXs"
        }
    )

    assert response.status_code == 401

    assert response.json() == {
            "success": False,
            "message": "Token Not Found"
        }

def test_refreh_token_hash_mismatch():

    response = client.post(
        "/refresh",
        params={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidHlwZSI6InJlZnJlc2giLCJqdGkiOiJhOGQ1YzZkMzNlMWUzMDMxYmUyNzI3MDc1Yzk0NGU4MSIsImV4cCI6MTc4ODE4MjAzN30.WzDH5x8ycP_p5udDTuvNPY1nyQFhrxp1vlcoA2wGUHM"
        }
    )

    assert response.status_code == 401

    assert response.json() == {
            "success": False,
            "message": "Invalid Token"
        }

def test_refresh_token_user_not_exist():

    response = client.post(
        "/refresh",
        params={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MSIsInR5cGUiOiJyZWZyZXNoIiwianRpIjoiYWM3Mzk1MmM0MDkwNjJjZjYwMDIzYWJkYmNkOTM1NmUiLCJleHAiOjE3ODgxODIzOTV9.EiXQ58xyGQ5HruBZSM-8ABOH8G8kNxw5SRBSe-txgj0"
        }
    )

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "message": "User Not Found"
    }
