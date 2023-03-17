import os
from pathlib import PosixPath

from opsml_artifacts.helpers import utils
from opsml_artifacts.helpers import gcp_utils

# from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.helpers.gcp_utils import GCPClient


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
    file_path = utils.FindPath.find_filepath(
        name="example.csv",
    )
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

    for blob in blobs:
        assert path in blob.name

    # delete
    storage_client.delete_object(
        gcs_bucket="test_bucket",
        blob_path=path,
    )


def test_gcp_scheduler_integration(mock_gcp_scheduler):
    payload = {
        "name": "test",
        "team": "test",
        "user_email": "test",
    }
    scheduler = gcp_utils.GCPMLScheduler()
    scheduler.submit_schedule(
        payload=payload,
        job_name="test",
        schedule="* * * * *",
        scheduler_uri="test",
        gcp_project="test",
        gcp_region="test",
    )
