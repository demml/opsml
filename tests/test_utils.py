import os
from pathlib import PosixPath

from opsml_data.helpers import utils
from opsml_data.helpers.defaults import params


def test_find_path():
    path = utils.FindPath.find_filepath("requirements.txt")
    assert isinstance(path, PosixPath)


def test_find_dir_path():
    path = utils.FindPath.find_dirpath(
        dir_name="example_project",
        path=os.getcwd(),
        anchor_file="anchor.py",
    )
    assert isinstance(path, str)


def test_find_src_dir():
    src_dir, src_path = utils.FindPath.find_source_dir(
        params.path,
        "anchor.py",
    )
    assert src_dir == "example_project"


def test_gcs_storage_client_integration():
    file_path = utils.FindPath.find_filepath(
        name="pick_time_example.csv",
    )
    # upload
    path = "test_upload/test.csv"

    storage_client = utils.GCSStorageClient(
        gcp_credentials=params.gcp_creds,
    )

    storage_client.upload(
        gcs_bucket=params.gcs_bucket,
        filename=file_path,
        destination_path=path,
    )

    # download
    storage_client.download_object(
        gcs_bucket=params.gcs_bucket,
        blob_path=path,
        destination_filename="test.csv",
    )

    blobs = storage_client.list_objects(
        gcs_bucket=params.gcs_bucket,
        prefix="test_upload/",
    )

    for blob in blobs:
        assert path in blob.name

    # delete
    storage_client.delete_object(
        gcs_bucket=params.gcs_bucket,
        blob_path=path,
    )

    # remove local
    os.remove("test.csv")
