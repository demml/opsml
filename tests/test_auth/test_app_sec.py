import pytest
from starlette.testclient import TestClient


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

    assert response.status_code == 403

    # try getting user
    response = test_app.post(
        "/opsml/auth/user",
        json={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 403

    # try updating user
    response = test_app.put(
        "/opsml/auth/user",
        json={"username": "test_user", "password": "test_password", "scopes": {"write": True}},
    )

    assert response.status_code == 403

    # try delete user
    response = test_app.delete(
        "/opsml/auth/user",
        params={"username": "test_user"},
    )

    assert response.status_code == 403
