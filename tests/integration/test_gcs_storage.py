import sys
from pathlib import Path

import pytest

from opsml.storage.client import StorageClient

pytestmark = [
    pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test"),
]


# gcs integration tests perform operation on test bucket that has a TTL of 1 day for all objects
def test_gcs_storage_client(tmp_path: Path, gcs_storage_client: StorageClient, gcs_test_bucket: Path) -> None:
    lpath = Path("tests/assets/cats.jpg")
    rpath_dir = gcs_test_bucket / "test_dir"
    rpath = rpath_dir / "cats.jpg"

    get_lpath = Path(tmp_path / "tests/assets/empty.cats.jpg")
    try:
        if gcs_storage_client.exists(rpath_dir):
            gcs_storage_client.rm(rpath_dir)
        assert not gcs_storage_client.exists(rpath_dir)

        with pytest.raises(FileNotFoundError):
            gcs_storage_client.ls(rpath_dir)

        # put
        gcs_storage_client.put(lpath, rpath)
        assert gcs_storage_client.exists(rpath)
        rpath_nested = rpath.parent / "nested/really/deep/cats-2.jpg"
        gcs_storage_client.put(lpath, rpath_nested)

        # ls
        assert len(gcs_storage_client.ls(gcs_test_bucket)) >= 1
        assert len(gcs_storage_client.ls(rpath_nested.parent)) >= 1

        # find
        assert gcs_storage_client.find(rpath_dir) == [rpath, rpath_nested]

        # get
        get_lpath = tmp_path / "cats.jpg"
        gcs_storage_client.get(rpath, get_lpath)
        assert get_lpath.exists()

        # iterfile
        for f in gcs_storage_client.iterfile(rpath, 1000):
            _ = lpath.read_bytes()

        # rm
        gcs_storage_client.rm(rpath)
        assert not gcs_storage_client.exists(rpath)
    finally:
        if gcs_storage_client.exists(rpath_dir):
            gcs_storage_client.rm(rpath_dir)


def test_gcs_storage_client_trees(tmp_path: Path, gcs_storage_client: StorageClient, gcs_test_bucket: Path) -> None:
    #
    # test.txt
    # child/
    #   test.txt
    #   grandchild/
    #     test.txt
    child = Path(tmp_path, "child")
    grand_child = Path(child, "grandchild")
    for path in [tmp_path, child, grand_child]:
        path.mkdir(parents=True, exist_ok=True)
        txt_path = Path(path, "test.txt")
        txt_path.write_text("hello, world")

    rpath_root = Path(gcs_test_bucket, "test_root")
    try:
        # ls
        if gcs_storage_client.exists(rpath_root):
            gcs_storage_client.rm(rpath_root)

        # put
        gcs_storage_client.put(tmp_path, rpath_root)
        assert len(gcs_storage_client.find(rpath_root)) == 3

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
        copy_dir = Path(rpath_root / "copy")
        gcs_storage_client.copy(rpath_root / "child", copy_dir)
        assert len(gcs_storage_client.find(copy_dir)) == 2

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
        put_dir = Path(rpath_root / "copy2")
        gcs_storage_client.put(tmp_path / "child", put_dir)
        assert len(gcs_storage_client.find(put_dir)) == 2

        # rm
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
        gcs_storage_client.rm(put_dir)
        assert len(gcs_storage_client.find(put_dir)) == 0
        with pytest.raises(FileNotFoundError):
            gcs_storage_client.ls(put_dir)

    finally:
        if gcs_storage_client.exists(rpath_root):
            gcs_storage_client.rm(rpath_root)
