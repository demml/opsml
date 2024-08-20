import pytest
from starlette.testclient import TestClient

from opsml.types.extra import User


@pytest.mark.appsec
def test_app_token(test_app: TestClient) -> None:
    """Test healthcheck with login"""

    response = test_app.get("/opsml/healthcheck")

    assert response.status_code == 401

    # get token
    response = test_app.post(
        "/opsml/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200

    # set bearer token
    token = response.json()["access_token"]
    test_app.headers.update({"Authorization": f"Bearer {token}"})

    # re-run healthcheck
    response = test_app.get("/opsml/healthcheck")
    assert response.status_code == 200


@pytest.mark.appsec
def test_app_user_mgmt(test_app: TestClient) -> None:
    """Test user management"""

    # get token
    response = test_app.post(
        "/opsml/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    # set bearer token
    token = response.json()["access_token"]
    test_app.headers.update({"Authorization": f"Bearer {token}"})

    # create user
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password"},
    )
    assert response.status_code == 200

    # get user
    response = test_app.get(
        "/opsml/auth/user",
        params={"username": "test_user"},
    )

    assert response.status_code == 200

    # Update user
    response = test_app.put(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password", "scopes": {"write": True}},
    )
    assert response.status_code == 200

    # delete user
    response = test_app.delete(
        "/opsml/auth/user",
        params={"username": "test_user"},
    )

    assert response.status_code == 200

    # get user that doesn't exist
    response = test_app.get(
        "/opsml/auth/user",
        params={"username": "not_exist"},
    )

    assert response.status_code == 404

    # delete user that doesn't exist
    response = test_app.delete(
        "/opsml/auth/user",
        params={"username": "not_exist"},
    )

    assert response.status_code == 404


@pytest.mark.appsec
def test_app_user_mgmt_creds(test_app: TestClient) -> None:
    """Test user management"""

    # get token for admin
    response = test_app.post(
        "/opsml/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    # set bearer token
    admin_token = response.json()["access_token"]
    test_app.headers.update({"Authorization": f"Bearer {admin_token}"})

    # create user (should only have read access)
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password"},
    )
    assert response.status_code == 200

    # create user (should only have read access)
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "another_user", "password": "test_password"},
    )
    assert response.status_code == 200

    # switch to test user
    response = test_app.post(
        "/opsml/auth/token",
        data={"username": "test_user", "password": "test_password"},
    )

    assert response.status_code == 200

    # set bearer token
    token = response.json()["access_token"]
    test_app.headers.update({"Authorization": f"Bearer {token}"})

    # try creating user
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "test_user2", "password": "test_password"},
    )

    assert response.status_code == 401

    # try getting user
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 401

    # try updating user (should pass given no permissions are changing)
    response = test_app.put(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password", "scopes": {"write": True}},
    )
    assert response.status_code == 200

    # try updating user (should fail)
    response = test_app.put(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password", "scopes": {"write": True, "admin": True}},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not enough permissions to change scopes"

    # try updating another user (should fail)
    response = test_app.put(
        "/opsml/auth/user",
        json={"username": "another_user", "password": "test_password", "scopes": {"write": True, "admin": True}},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not enough permissions"

    # try delete user
    response = test_app.delete(
        "/opsml/auth/user",
        params={"username": "test_user"},
    )

    assert response.status_code == 403


@pytest.mark.appsec
def test_refresh_token(test_app: TestClient) -> None:
    """Test token refreshing"""

    assert test_app.get("/opsml/auth/token/rotate").status_code == 404
    assert test_app.get("/opsml/auth/token/refresh").status_code == 401

    response = test_app.post(
        "/opsml/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    refresh_token = response.cookies.get("refresh_token")
    access_token = response.json()["access_token"]

    assert test_app.get("/opsml/auth/token/rotate").status_code == 200
    assert test_app.get("/opsml/auth/token/refresh").status_code == 200


@pytest.mark.appsec
def test_user_routes(test_app: TestClient) -> None:
    # get token for admin
    response = test_app.post(
        "/opsml/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    # set bearer token
    admin_token = response.json()["access_token"]
    test_app.headers.update({"Authorization": f"Bearer {admin_token}"})

    # create user (should only have read access)
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password"},
    )
    assert response.status_code == 200

    response = test_app.get(
        "/opsml/auth/user/exists",
        params={"username": "test_user"},
    )

    assert response.status_code == 200
    assert response.json()["exists"] == True

    response = test_app.get(
        "/opsml/auth/user/exists",
        params={"username": "missing_user"},
    )

    assert response.status_code == 200
    assert response.json()["exists"] == False


@pytest.mark.appsec
def test_create_user(test_app: TestClient) -> None:
    
    response = test_app.post(
        "/opsml/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    # set bearer token
    admin_token = response.json()["access_token"]
    test_app.headers.update({"Authorization": f"Bearer {admin_token}"})

    # create user (should only have read access)
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password"},
    )
    assert response.status_code == 200

    user = User(
        username="test_user",
        password="test_password",
        security_question="test_question",
        security_answer="test_answer",
        email="demml@opsml.com",
        full_name="test user",
    )

    response = test_app.post(
        "/opsml/auth/register",
        json=user.model_dump(),
    )

    assert response.status_code == 409
    
    user.username = "new_user"

    response = test_app.post(
        "/opsml/auth/register",
        json=user.model_dump(),
    )

    assert response.status_code == 200
    assert response.json()["created"] == True
    
    
    # test temp token
    response = test_app.post(
        "/opsml/auth/temp",
        json={"username": "new_user", "answer": "test_answer"},
    )
    
    assert response.status_code == 200
    
    
    # test temp token with wrong answer
    response = test_app.post(
        "/opsml/auth/temp",
        json={"username": "new_user", "answer": "test_answer_fail"},
    )
    
    assert response.status_code == 200
    assert response.json() == "Incorrect answer"
    
    # test temp token with wrong user
    response = test_app.post(
        "/opsml/auth/temp",
        json={"username": "no_user", "answer": "test_answer_fail"},
    )
    
    assert response.status_code == 200
    assert response.json() == "User not found"