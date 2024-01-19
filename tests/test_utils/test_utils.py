import base64
import json
import sys
from pathlib import Path
from typing import Any

import pytest
from google.oauth2.service_account import Credentials

from opsml.helpers import exceptions, gcp_utils, utils


def test_experimental_feature() -> None:
    called = False

    @utils.experimental_feature
    def test(self: Any) -> None:
        nonlocal called
        called = True

    test(1)
    assert called


def test_clean_string() -> None:
    assert utils.clean_string("  TEST ") == "test"
    assert utils.clean_string("  !!test!!  ") == "test"
    assert utils.clean_string("  !!_-test-_!!  ") == "--test--"


def test_validate_repository_name_pattern() -> None:
    utils.validate_name_repository_pattern("test", "test")
    utils.validate_name_repository_pattern("test-name", "test-repository")

    with pytest.raises(ValueError):
        utils.validate_name_repository_pattern("TEST", "test")

    with pytest.raises(ValueError):
        utils.validate_name_repository_pattern("test:", "test")

    with pytest.raises(ValueError):
        utils.validate_name_repository_pattern("test_name", "test")


def test_type_checker_check_metric_type() -> None:
    assert utils.TypeChecker.check_metric_type(1) == 1
    assert utils.TypeChecker.check_metric_type(1.0) == 1.0

    with pytest.raises(ValueError):
        utils.TypeChecker.check_metric_type("test")


def test_type_checker_check_param_type() -> None:
    assert utils.TypeChecker.check_param_type(1) == 1
    assert utils.TypeChecker.check_param_type(1.0) == 1.0
    assert utils.TypeChecker.check_param_type("test") == "test"

    with pytest.raises(ValueError):
        utils.TypeChecker.check_metric_type((1, 1))


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_file_utils_find_dirpath(tmp_path: Path) -> None:
    tmp_assets = Path(tmp_path).joinpath("test/child/grandchild")
    tmp_assets.mkdir(parents=True)
    tmp_assets.joinpath("test.txt").write_text("hello, world", encoding="utf-8")

    assert Path(tmp_assets).joinpath("test.txt").exists()

    assert utils.FileUtils.find_dirpath(path=tmp_path, dir_name="test", anchor_file="test.txt").name == "test"
    assert utils.FileUtils.find_dirpath(path=tmp_path, dir_name="child", anchor_file="test.txt").name == "child"
    assert (
        utils.FileUtils.find_dirpath(path=tmp_path, dir_name="grandchild", anchor_file="test.txt").name == "grandchild"
    )

    # Create a second "anchor_file" somewhere in the directory tree. Any search
    # where the anchor file exists in more than one directory rooted at tmp_path
    # will fail.
    #
    # /tmp_dir/test/child/gradchild/test.text
    # /tmp_dir/test/child2/test.txt
    #
    tmp_assets2 = Path(tmp_path).joinpath("test/child2")
    tmp_assets2.mkdir()
    tmp_assets2.joinpath("test.txt").write_text("hello, world", encoding="utf-8")
    assert Path(tmp_assets2).joinpath("test.txt").exists()

    with pytest.raises(exceptions.MoreThanOnePathException):
        utils.FileUtils.find_dirpath(path=tmp_path, dir_name="child2", anchor_file="test.txt")

    with pytest.raises(FileNotFoundError):
        # `path` does not exist
        utils.FileUtils.find_dirpath(path="/notthere", dir_name="test", anchor_file="test.txt")

    with pytest.raises(FileNotFoundError):
        # `path` exists, but `dir_name` does not. Not we are searching tmp_assets2, not tmp_path - test.txt is unique.
        utils.FileUtils.find_dirpath(path=tmp_assets2, dir_name="notthere", anchor_file="test.txt")


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_file_utils_find_filepath(tmp_path: Path) -> None:
    tmp_files = Path(tmp_path).joinpath("files")
    tmp_files.mkdir()

    tmp_file = Path(tmp_files / "test.txt")
    tmp_file.write_text("hello, world", encoding="utf-8")

    assert utils.FileUtils.find_filepath("test.txt", path=str(tmp_files)) is not None
    with pytest.raises(FileNotFoundError):
        utils.FileUtils.find_filepath("notthere", path=str(tmp_files))

    tmp_files_2 = Path(tmp_path).joinpath("files2")
    tmp_files_2.mkdir()
    tmp_file2 = Path(tmp_files_2 / "test.txt")
    tmp_file2.write_text("hello, world", encoding="utf-8")

    with pytest.raises(exceptions.MoreThanOnePathException):
        utils.FileUtils.find_filepath("test.txt", path=str(tmp_path))


def test_all_sublcasses() -> None:
    class A:
        pass

    class B(A):
        pass

    class C(B):
        pass

    subs = utils.all_subclasses(A)
    assert B in subs and C in subs


def test_check_package_exists() -> None:
    assert utils.check_package_exists("pydantic")
    assert not utils.check_package_exists("notthere")


def test_gcp_creds(gcp_cred_path: str):
    with open(gcp_cred_path) as creds:
        creds = json.load(creds)

    json_creds = json.dumps(creds)
    base64_creds = base64.b64encode(json_creds.encode("utf-8")).decode("utf-8")
    creds, project = gcp_utils.GcpCredsSetter(service_creds=base64_creds).get_base64_creds()

    assert isinstance(creds, Credentials)


def test_import_exception():
    with pytest.raises(ModuleNotFoundError):
        utils.try_import("fail", "fail", "fail")
