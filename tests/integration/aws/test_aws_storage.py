import sys
from pathlib import Path

import pytest

from opsml.storage.client import StorageClient

pytestmark = [
    pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test"),
]


# azure integration tests perform operation on test bucket that has a TTL of 1 day for all objects
def test_aws_storage_client(tmp_path: Path, aws_storage_client: StorageClient, aws_s3_bucket: Path) -> None:
    lpath = Path("tests/assets/cats.jpg")
    rpath_dir = aws_s3_bucket / "test_dir"
    rpath = rpath_dir / "cats.jpg"

    get_lpath = Path(tmp_path / "tests/assets/empty.cats.jpg")
    try:
        if aws_storage_client.exists(rpath_dir):
            aws_storage_client.rm(rpath_dir)
        assert not aws_storage_client.exists(rpath_dir)

        with pytest.raises(FileNotFoundError):
            aws_storage_client.ls(rpath_dir)

        # put
        aws_storage_client.put(lpath, rpath)
        assert aws_storage_client.exists(rpath)
        rpath_nested = rpath.parent / "nested/really/deep/cats-2.jpg"
        aws_storage_client.put(lpath, rpath_nested)

        # generate_presigned_url
        # get bucket
        blob_path = rpath.relative_to(aws_s3_bucket)
        path = aws_storage_client.generate_presigned_url(blob_path, 1)
        assert path is not None

        # ls
        assert len(aws_storage_client.ls(aws_s3_bucket)) >= 1
        assert len(aws_storage_client.ls(rpath_nested.parent)) >= 1

        # find
        assert aws_storage_client.find(rpath_dir) == [rpath, rpath_nested]

        # get
        get_lpath = tmp_path / "cats.jpg"
        aws_storage_client.get(rpath, get_lpath)
        assert get_lpath.exists()

        # iterfile
        for f in aws_storage_client.iterfile(rpath, 1000):
            _ = lpath.read_bytes()

        # rm
        aws_storage_client.rm(rpath)
        assert not aws_storage_client.exists(rpath)
    finally:
        if aws_storage_client.exists(rpath_dir):
            aws_storage_client.rm(rpath_dir)


def test_aws_storage_client_trees(tmp_path: Path, aws_storage_client: StorageClient, aws_s3_bucket: Path) -> None:
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

    rpath_root = Path(aws_s3_bucket, "test_root")
    try:
        # ls
        if aws_storage_client.exists(rpath_root):
            aws_storage_client.rm(rpath_root)

        # put
        aws_storage_client.put(tmp_path, rpath_root)
        assert len(aws_storage_client.find(rpath_root)) == 3

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
        aws_storage_client.copy(rpath_root / "child", copy_dir)
        assert len(aws_storage_client.find(copy_dir)) == 2

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
        aws_storage_client.put(tmp_path / "child", put_dir)
        assert len(aws_storage_client.find(put_dir)) == 2

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
        aws_storage_client.rm(put_dir)
        assert len(aws_storage_client.find(put_dir)) == 0
        with pytest.raises(FileNotFoundError):
            aws_storage_client.ls(put_dir)

    finally:
        if aws_storage_client.exists(rpath_root):
            aws_storage_client.rm(rpath_root)
