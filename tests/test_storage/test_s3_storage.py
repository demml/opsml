from pathlib import Path
from unittest.mock import patch

from opsml.settings.config import OpsmlConfig
from opsml.storage import client


def test_s3_presigned_uri():
    class MockS3Client:
        def __init__(self, *args, **kwargs):
            pass

        def generate_presigned_url(self, *args, **kwargs):
            return "https://fake.com"

    with patch("boto3.client", return_value=MockS3Client()), patch(
        "s3fs.S3FileSystem",
        autospec=True,
    ):
        cfg = OpsmlConfig(opsml_tracking_uri="./mlruns", opsml_storage_uri="s3://fake")
        storage_client = client.get_storage_client(cfg)
        assert isinstance(storage_client, client.S3StorageClient)

        signed_url = storage_client.generate_presigned_url(Path("fake"), 1)
        assert signed_url == "https://fake.com"

    # this should result in an error (None)
    with patch(
        "boto3.client",
        return_value=None,
    ):
        cfg = OpsmlConfig(opsml_tracking_uri="./mlruns", opsml_storage_uri="s3://fake")
        storage_client = client.get_storage_client(cfg)
        signed_url = storage_client.generate_presigned_url(Path("fake"), 1)
        assert signed_url is None
