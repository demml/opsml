import pytest
from unittest.mock import patch
import httpx
import joblib
import numpy as np
from opsml_artifacts.helpers.gcp_utils import GCPMLScheduler, GCSStorageClient
from pydantic import BaseModel

################ Test Classes
class Blob(BaseModel):
    name: str = "test_upload/test.csv"

    def download_to_filename(self, destination_filename):
        return True

    def upload_from_filename(self, filename):
        return True

    def delete(self):
        return True


class Bucket(BaseModel):
    name: str = "bucket"

    def blob(self, path: str):
        return Blob()

    def list_blobs(self, prefix: str):
        return [Blob()]


@pytest.fixture(scope="function")
def mock_gcs_storage_response():
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                "storage_type": "gcs",
                "storage_uri": "gs://test",
            }

    class MockHTTPX(httpx.Client):
        def get(self, url, **kwargs):
            return MockResponse()

    with patch("httpx.Client", MockHTTPX) as mock_requests:
        yield mock_requests


@pytest.fixture(scope="function")
def load_transformer_example():
    import tensorflow as tf

    loaded_model = tf.keras.models.load_model("tests/assets/transformer_example")
    data = np.load("tests/assets/transformer_data.npy")
    return loaded_model, data


@pytest.fixture(scope="function")
def load_multi_input_keras_example():
    import tensorflow as tf

    loaded_model = tf.keras.models.load_model("tests/assets/multi_input_example")
    data = joblib.load("tests/assets/multi_input_data.joblib")
    return loaded_model, data


@pytest.fixture(scope="function")
def load_pytorch_resnet():
    import torch

    loaded_model = torch.load("tests/assets/resnet.pt")
    data = torch.randn(1, 3, 224, 224).numpy()

    return loaded_model, data


@pytest.fixture(scope="function")
def mock_gcp_scheduler():
    class ScheduleClient:
        def common_location_path(self, project: str, location: str):
            return f"{project}-{location}"

        def list_jobs(self, parent: str):
            return [Blob(name="test")]

        def delete_job(self, job_name: str):
            return True

        def create_job(self, parent: str, job: str):
            return "test_job"

    class MockScheduler(GCPMLScheduler):
        def __init__(self):
            self.schedule_client = ScheduleClient()
            self.oidc_token = "test"
            self.parent_path = "test"

        def _create_job_class(self, job: dict):
            return "job"

    with patch("opsml_artifacts.helpers.gcp_utils.GCPMLScheduler", MockScheduler) as mock_scheduler:

        yield mock_scheduler


@pytest.fixture(scope="function")
def mock_gcs(test_df):
    class StorageClient:
        def bucket(self, gcs_bucket: str):
            return Bucket()

        def blob(self, blob_path: str):
            return Blob()

        def list_blobs(self, prefix: str):
            return [Blob(), Blob()]

    class MockStorage(GCSStorageClient):
        def __init__(self):
            self.client = StorageClient()

    with patch("opsml_artifacts.helpers.gcp_utils.GCSStorageClient", MockStorage) as mock_storage:
        yield mock_storage
