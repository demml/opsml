from pathlib import Path

import pytest

from opsml.storage.client import GCSFSStorageClient


# gcs integration tests perform operation on test bucket that has a TTL of 1 day for all objects
@pytest.mark.integration
def test_gcsfs_integration(tmp_path: Path, gcs_storage_client: GCSFSStorageClient, gcs_test_bucket: Path):
    lpath = Path("tests/assets/cats.jpg")
    rpath = gcs_test_bucket / "cats.jpg"

    get_lpath = Path(tmp_path / "tests/assets/empty.cats.jpg")
    try:
        # put file
        gcs_storage_client.put(lpath, rpath)

        # check file exists
        assert gcs_storage_client.exists(rpath)

        # deep tree
        rpath_nested = rpath.parent / "nested/really/deep/cats-2.jpg"
        gcs_storage_client.put(lpath, rpath_nested)

        # list files (not recursive)
        assert len(gcs_storage_client.ls(gcs_test_bucket)) >= 1
        assert len(gcs_storage_client.ls(rpath_nested.parent)) >= 1
        with pytest.raises(FileNotFoundError):
            assert len(gcs_storage_client.ls(gcs_test_bucket / "notthere")) == 0

        # find file
        assert gcs_storage_client.find(rpath) == [rpath]

        # get file
        get_lpath = Path("tests/assets/empty/cats.jpg")
        gcs_storage_client.get(rpath, get_lpath)
        assert get_lpath.exists()

        # check iterfile
        for f in gcs_storage_client.iterfile(rpath, 1000):
            _ = lpath.read_bytes()

        # remove file
        gcs_storage_client.rm(rpath)

        # assert file is removed
        assert not gcs_storage_client.exists(rpath)
    finally:
        if gcs_storage_client.exists(rpath):
            gcs_storage_client.rm(rpath)
        get_lpath.unlink(missing_ok=True)
