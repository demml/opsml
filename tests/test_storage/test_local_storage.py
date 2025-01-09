import sys
from pathlib import Path

import pytest

from opsml.storage.client import StorageClient, StorageClientBase

pytestmark = [pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")]


def test_local_storage_client_crud(tmp_path: Path, local_storage_client: StorageClient):
    # The local storage client can write *anywhere*, it's not chrooted. Not
    # ideal.

    # ls
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

    # put
    local_storage_client.put(lpath, rpath)
    local_storage_client.put(lpath, rpath)  # verify overwrite
    assert local_storage_client.exists(rpath)

    # copy
    local_storage_client.copy(rpath, rpath2)
    assert local_storage_client.exists(rpath2)
    assert len(local_storage_client.find(tmp_path)) == 2
    assert [rpath, rpath2] == local_storage_client.find(tmp_path)

    # # get
    get_lpath = Path(tmp_path / "child/cats.jpg")
    local_storage_client.get(rpath, get_lpath)
    assert local_storage_client.exists(get_lpath)
    local_storage_client.rm(get_lpath)

    # rm
    local_storage_client.rm(rpath)
    with pytest.raises(FileNotFoundError):
        local_storage_client.rm(invalid_path)
    assert len(local_storage_client.find(tmp_path)) == 1
    assert rpath2 == local_storage_client.find(tmp_path)[0]

    # open
    txt_path: Path = tmp_path / "test.txt"
    txt_path.write_text("hello, world")
    with local_storage_client.open(txt_path, mode="r") as f:
        assert "hello, world" == f.read()


def test_local_storage_client_trees(tmp_path: Path, local_storage_client: StorageClient):
    child = Path(tmp_path, "child")
    grand_child = Path(child, "grandchild")
    for path in [tmp_path, child, grand_child]:
        path.mkdir(parents=True, exist_ok=True)
        Path(path, "test.txt").write_text("hello, world")

        # exists
        assert local_storage_client.exists(path)

        # ls
        assert len(local_storage_client.ls(path)) == 1

    # find
    assert len(local_storage_client.find(tmp_path)) == 3

    # copy
    #
    # test.txt
    # child/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy/
    #   test.txt
    #   grandchild/
    #     test.txt
    copy_dir = Path(tmp_path / "copy")
    local_storage_client.copy(tmp_path / "child", copy_dir)
    assert len(local_storage_client.find(copy_dir)) == 2

    # get
    #
    # test.txt
    # child/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy2/
    #   test.txt
    #   grandchild/
    #     test.txt

    get_dir = Path(tmp_path / "copy2")
    local_storage_client.get(tmp_path / "child", get_dir)
    assert len(local_storage_client.find(get_dir)) == 2

    # put
    #
    # test.txt
    # child/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy2/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy3/
    #   test.txt
    #   grandchild/
    #     test.txt
    put_dir = Path(tmp_path / "copy3")
    local_storage_client.put(tmp_path / "child", put_dir)
    assert len(local_storage_client.find(put_dir)) == 2

    # rm
    #
    # test.txt
    # copy/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy2/
    #   test.txt
    #   grandchild/
    #     test.txt
    # copy3/
    #   test.txt
    #   grandchild/
    #     test.txt
    local_storage_client.rm(tmp_path / "child")
    assert not local_storage_client.exists(tmp_path / "child")


def test_local_storage_client_presigned_uri(local_storage_client: StorageClient):
    path = local_storage_client.generate_presigned_url(Path("fake"), 1)
    assert path == "/artifacts/fake"

    base = StorageClientBase(settings=local_storage_client.settings)
    path = base.generate_presigned_url(Path("fake"), 1)
    assert path == "fake"
