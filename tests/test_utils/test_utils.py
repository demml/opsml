import os
from pathlib import PosixPath
import base64
from opsml.helpers import utils
from opsml.helpers import gcp_utils
from google.oauth2.service_account import Credentials
import json
import pytest


def test_find_path():
    path = utils.FindPath.find_filepath("requirements.txt")
    assert isinstance(path, PosixPath)


def test_find_dir_path():
    path = utils.FindPath.find_dirpath(
        dir_name="assets",
        path=os.getcwd(),
        anchor_file="anchor.py",
    )
    assert isinstance(path, str)


def test_find_src_dir():
    src_dir, src_path = utils.FindPath.find_source_dir(
        os.getcwd(),
        "anchor.py",
    )
    assert src_dir == "assets"


def test_gcs_storage_client_integration(mock_gcs):
    FILENAME = "example.csv"
    file_path = utils.FindPath.find_filepath(name=FILENAME)

    # upload
    path = "test_upload/test.csv"
    #
    storage_client = gcp_utils.GCSStorageClient()
    #
    storage_client.upload(
        gcs_bucket="test_bucket",
        filename=file_path,
        destination_path=path,
    )
    #
    # download
    storage_client.download_object(
        gcs_bucket="test_bucket",
        blob_path=path,
        destination_filename="test.csv",
    )
    #
    blobs = storage_client.list_objects(
        gcs_bucket="test_bucket",
        prefix="test_upload/",
    )

    _ = storage_client.download_object_from_uri(gcs_uri="gs://test_bucket/test_upload/test.csv")

    storage_client.delete_object_from_uri(gcs_uri="gs://test_bucket/test_upload/test.csv")

    for blob in blobs:
        assert path in blob.name

    bucket, path, file_ = storage_client.parse_gcs_uri("gs://testbucket/blob/example.csv")

    assert file_ == FILENAME

    # delete
    storage_client.delete_object(
        gcs_bucket="test_bucket",
        blob_path=path,
    )


def test_gcp_creds(gcp_cred_path: str):
    with open(gcp_cred_path) as creds:
        creds = json.load(creds)

    json_creds = json.dumps(creds)
    base64_creds = base64.b64encode(json_creds.encode("utf-8")).decode("utf-8")
    creds, project = gcp_utils.GcpCredsSetter(service_creds=base64_creds).get_base64_creds()

    assert isinstance(creds, Credentials)


def test_gcp_default_creds(gcp_cred_path: str):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_cred_path

    creds, project = gcp_utils.GcpCredsSetter().get_base64_creds()

    assert isinstance(creds, Credentials)


def test_import_exception():
    with pytest.raises(ModuleNotFoundError):
        utils.try_import("fail", "fail", "fail")
