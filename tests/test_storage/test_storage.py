from pathlib import Path

import pytest

from opsml.storage.client import StorageClient


def test_local_storage_client_crud(tmp_path: Path, local_storage_client: StorageClient):
    # The local storage client can write *anywhere*, it's not chrooted. Not
    # ideal.
    assert local_storage_client.exists(tmp_path)
    assert len(local_storage_client.ls(tmp_path)) == 0

    invalid_path = tmp_path.joinpath("notthere")
    assert not local_storage_client.exists(invalid_path)
    with pytest.raises(FileNotFoundError):
        local_storage_client.ls(invalid_path)

    # find should *not* throw FileNotFoundError
    assert len(local_storage_client.find(tmp_path)) == 0
    assert len(local_storage_client.find(invalid_path)) == 0

    lpath = Path("./tests/assets/cats.jpg")
    rpath = Path(tmp_path, "cats.jpg")
    rpath2 = Path(tmp_path, "some/nested/folder/structure/cats.jpg")

    local_storage_client.put(lpath, rpath)
    assert local_storage_client.exists(rpath)

    local_storage_client.copy(rpath, rpath2)
    assert local_storage_client.exists(rpath2)
    assert len(local_storage_client.find(tmp_path)) == 2


def test_local_storage_client_trees(tmp_path: Path, local_storage_client: StorageClient):
    pass
