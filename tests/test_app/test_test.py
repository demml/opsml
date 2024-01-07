import sys

import pytest
from fastapi.exceptions import HTTPException
from starlette.testclient import TestClient

from opsml.app.core.dependencies import swap_opsml_root
from opsml.storage.api import ApiRoutes

EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)


def test_registry_name_fail(test_app: TestClient):
    response = test_app.get(
        "/opsml/registry/table",
        params={"registry_type": "blah"},
    )

    assert response.status_code == 500


def test_upload_fail(test_app: TestClient):
    headers = {
        "Filename": "blah:",
        "WritePath": "fake",
        "X-Prod-Token": "test-token",
    }
    files = {"file": open("tests/assets/cats.jpg", "rb")}

    response = test_app.post(
        url=f"opsml/{ApiRoutes.UPLOAD}",
        files=files,
        headers=headers,
    )

    assert response.status_code == 422


def test_download_fail(test_app: TestClient):
    # test register model (onnx)
    response = test_app.get(url=f"opsml/{ApiRoutes.DOWNLOAD_FILE}?read_path=fake")
    assert response.status_code == 422


def test_verify_path():
    swap_opsml_root("opsml-root:/test/assets/OPSML_MODEL_REGISTRY")
    swap_opsml_root("opsml-root:/test/assets/OPSML_DATA_REGISTRY")
    swap_opsml_root("opsml-root:/test/assets/OPSML_RUN_REGISTRY")
    swap_opsml_root("opsml-root:/test/assets/OPSML_PROJECT_REGISTRY")

    with pytest.raises(HTTPException):
        assert swap_opsml_root("opsml-root:/tests/assets/fake")
