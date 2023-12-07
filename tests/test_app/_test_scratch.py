

from starlette.testclient import TestClient



def test_card_create_fail(test_app: TestClient):
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/create",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


def test_card_update_fail(test_app: TestClient):
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/update",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


def test_card_list_fail(test_app: TestClient):
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/list",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500
