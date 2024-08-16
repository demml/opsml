from fastapi.testclient import TestClient


def test_heartbeat(test_app: TestClient) -> None:
    """Test opsml registry app healthcheck
    Args:
        test_app:
            FastAPI test client
    """
    response = test_app.get("/opsml/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"is_alive": True}
