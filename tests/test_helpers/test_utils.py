import os
import sys
from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.helpers import utils
from opsml.registry.storage.client import StorageClient


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_local_paths(tmp_path: Path, storage_client: StorageClient):
    FILENAME = "example.csv"
    file_path = utils.FileUtils.find_filepath(name=FILENAME)

    dest_path = tmp_path.joinpath(FILENAME)
    storage_client.upload(local_path=file_path, write_path=str(dest_path))

    assert dest_path.exists() and dest_path.is_file()

    dir_path = utils.FileUtils.find_dirpath(
        path=os.getcwd(),
        dir_name="assets",
        anchor_file=FILENAME,
    )
    dest_path = tmp_path.joinpath("assets")
    storage_client.upload(local_path=str(dir_path), write_path=str(dest_path))

    assert dest_path.exists() and dest_path.is_dir()
