import os
import pathlib
import shutil
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

# running tests similar to opsml
# just to make sure everything works
DB_FILE_PATH = str(pathlib.Path.home().joinpath("tmp.db"))
SQL_PATH = f"sqlite:///{DB_FILE_PATH}"
STORAGE_PATH = str(pathlib.Path.home().joinpath("opsml_registries"))

os.environ["OPSML_TRACKING_URI"] = SQL_PATH
os.environ["OPSML_STORAGE_URI"] = STORAGE_PATH


def cleanup() -> None:
    """Removes temp files"""

    if os.path.exists(DB_FILE_PATH):
        os.remove(DB_FILE_PATH)

    # remove api mlrun path
    shutil.rmtree(STORAGE_PATH, ignore_errors=True)

    # remove test experiment mlrun path
    shutil.rmtree("opsml_registries", ignore_errors=True)


@pytest.fixture(scope="module")
def test_app() -> Iterator[TestClient]:
    cleanup()
    from opsml.app.main import OpsmlApp  # pylint: disable=import-outside-toplevel

    opsml_app = OpsmlApp()
    with TestClient(opsml_app.get_app()) as tc:
        yield tc
    cleanup()
