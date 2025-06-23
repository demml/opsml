from fastapi.testclient import TestClient
from tests.api.conftest import PredictRequest, create_app
import shutil
import os
from tests.conftest import WINDOWS_EXCLUDE
import pytest


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_api(create_artifacts):
    # create the client
    opsml_app, lock_file = create_artifacts

    # create fastapi app
    fastapi_app = create_app(opsml_app)

    # Configure the TestClient
    with TestClient(fastapi_app) as client:
        # Simulate requests
        for _ in range(60):
            response = client.post(
                "/predict",
                json=PredictRequest.example_request(),
            )
        assert response.status_code == 200

    shutil.rmtree(opsml_app)
    os.remove(lock_file)
