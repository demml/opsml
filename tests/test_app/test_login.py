import sys

from starlette.testclient import TestClient


DARWIN_EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


def test_app_with_login(test_app_login: TestClient) -> None:
    """Test healthcheck with login"""

    response = test_app_login.get("/opsml/healthcheck")

    assert response.status_code == 200
