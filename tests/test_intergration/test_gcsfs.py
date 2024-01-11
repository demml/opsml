import os
from pathlib import Path

import pytest

from opsml.storage.client import GCSFSStorageClient


# gcs integration tests perform operation on test bucket that has a TTL of 1 day for all objects
@pytest.mark.integration
def test_gcsfs_integration(gcs_storage_client: GCSFSStorageClient, gcs_test_bucket: Path):
    lpath = Path("tests/assets/cats.jpg")
    rpath = gcs_test_bucket / "cats.jpg"

    try:
        # put file
        gcs_storage_client.put(lpath, rpath)

        # check file exists
        assert gcs_storage_client.exists(rpath)

        # list files
        files = gcs_storage_client.ls(gcs_test_bucket)
        assert len(files) >= 1

        # find file
        assert gcs_storage_client.find(rpath) == [rpath.as_posix()]

        # get file
        get_lpath = Path("tests/assets/empty/cats.jpg")
        gcs_storage_client.get(rpath, get_lpath)
        assert get_lpath.exists()

        # remove local file
        os.remove(get_lpath.as_posix())

        # check iterfile
        for f in gcs_storage_client.iterfile(rpath, 1000):
            _bytes = lpath.read_bytes()

        # remove file
        gcs_storage_client.rm(rpath)

        # assert file is removed
        assert not gcs_storage_client.exists(rpath)
    finally:
        if gcs_storage_client.exists(rpath):
            gcs_storage_client.rm(rpath)
