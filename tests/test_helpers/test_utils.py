import os
import sys
from pathlib import Path

import pytest

from opsml.helpers import utils
from opsml.storage.client import StorageClient


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_local_paths(tmp_path: Path, local_storage_client: StorageClient):
    FILENAME = "example.csv"
    file_path = utils.FileUtils.find_filepath(name=FILENAME)

    dest_path = tmp_path.joinpath(FILENAME)
    local_storage_client.put(file_path, dest_path)

    assert dest_path.exists() and dest_path.is_file()

    dir_path = utils.FileUtils.find_dirpath(
        path=os.getcwd(),
        dir_name="assets",
        anchor_file=FILENAME,
    )
    dest_path = tmp_path.joinpath("assets")
    local_storage_client.put(dir_path, dest_path)

    assert dest_path.exists() and dest_path.is_dir()


def test_create_temp_save_path() -> None:
    with utils.FileUtils.create_tmp_path("/some/long/path/with/file.txt") as tmp_path:
        tmp_path = Path(tmp_path)
        assert tmp_path.parent.exists() and tmp_path.parent.is_dir() and tmp_path.name == "file.txt"
