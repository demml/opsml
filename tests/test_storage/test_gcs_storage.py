from pathlib import Path
from unittest.mock import patch

from opsml.helpers import gcp_utils
from opsml.settings.config import OpsmlConfig
from opsml.storage import client


def test_gcs_presigned_uri() -> None:
    class MockBlob:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def generate_signed_url(self, *args, **kwargs) -> str:
            return "https://fake.com"

    class MockBucket:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def blob(self, *args, **kwargs) -> MockBlob:
            return MockBlob()

    class MockGCSClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def bucket(self, *args, **kwargs) -> MockBucket:
            return MockBucket()

    with (
        patch(
            "opsml.helpers.gcp_utils.GcpCredsSetter.get_creds",
            return_value=gcp_utils.GcpCreds(default_creds=True),
        ),
        patch(
            "google.auth.transport.requests.Request",
            return_value=None,
        ),
        patch(
            "google.auth.compute_engine.IDTokenCredentials",
            autospec=True,
        ),
        patch(
            "gcsfs.GCSFileSystem",
            autospec=True,
        ),
        patch(
            "google.cloud.storage.Client",
            return_value=MockGCSClient(),
        ),
    ):
        cfg = OpsmlConfig(opsml_tracking_uri="./opsml_registries", opsml_storage_uri="gs://fake")
        storage_client = client.get_storage_client(cfg)
        assert isinstance(storage_client, client.GCSFSStorageClient)

        signed_url = storage_client.generate_presigned_url(Path("fake"), 1)
        assert signed_url == "https://fake.com"

    # this should result in an error (None)
    with (
        patch(
            "opsml.helpers.gcp_utils.GcpCredsSetter.get_creds",
            return_value=gcp_utils.GcpCreds(default_creds=True),
        ),
        patch(
            "gcsfs.GCSFileSystem",
            autospec=True,
        ),
        patch(
            "google.auth.transport.requests.Request",
            return_value=None,
        ),
        patch(
            "google.cloud.storage.Client",
            return_value=MockGCSClient(),
        ),
    ):
        cfg = OpsmlConfig(opsml_tracking_uri="./opsml_registries", opsml_storage_uri="gs://fake")
        storage_client = client.get_storage_client(cfg)
        assert isinstance(storage_client, client.GCSFSStorageClient)

        signed_url = storage_client.generate_presigned_url(Path("fake"), 1)
        assert signed_url is None
