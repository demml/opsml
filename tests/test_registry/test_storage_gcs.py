import json

import numpy as np
import pyarrow as pa
import pytest

from opsml.registry.storage.artifact import (
    ArtifactStorageType,
    JSONStorage,
    NumpyStorage,
    ParquetStorage,
)
from opsml.registry.storage.client import StorageClient
from tests import conftest

pytestmark = pytest.mark.skip(reason="Requires live GCS credentials")


def test_gcs_parquet(real_gcs: StorageClient, test_arrow_table) -> None:
    pq_writer = ParquetStorage(
        storage_client=real_gcs,
        artifact_type=ArtifactStorageType.PYARROW,
    )

    uri = pq_writer.save_artifact(
        artifact=test_arrow_table,
        root_uri=conftest.save_path(),
        filename="test",
    )

    table = pq_writer.load_artifact(uri)
    assert isinstance(table, pa.Table)


def test_gcs_numpy(real_gcs: StorageClient, test_array):
    numpy_writer = NumpyStorage(
        storage_client=real_gcs,
        artifact_type=ArtifactStorageType.NUMPY,
    )
    uri = numpy_writer.save_artifact(
        artifact=test_array,
        root_uri=conftest.save_path(),
        filename="test",
    )

    array = numpy_writer.load_artifact(storage_uri=uri)
    assert isinstance(array, np.ndarray)


def test_gcs_json(real_gcs: StorageClient):
    # Data to be written
    dictionary = {
        "id": "04",
        "name": "test",
    }

    # Serializing json
    json_object = json.dumps(dictionary, indent=4)

    json_writer = JSONStorage(
        artifact_type=ArtifactStorageType.JSON,
        storage_client=real_gcs,
    )
    uri = json_writer.save_artifact(
        artifact=json_object,
        root_uri=conftest.save_path(),
        filename="test",
    )

    loaded_json = json_writer.load_artifact(storage_uri=uri)

    assert loaded_json == dictionary


# @pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
# def test_api_pytorch_model(storage_client, load_pytorch_resnet):
#     model, data = load_pytorch_resnet

#     model_storage = PyTorchModelStorage(
#         artifact_type=ArtifactStorageType.PYTORCH,
#         storage_client=storage_client,
#     )

#     uri = model_storage.save_artifact(
#         artifact=model,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )

#     loaded_model = model_storage.load_artifact(storage_uri=uri)
#     assert isinstance(loaded_model, type(model))


# @pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
# @pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
# def test_api_tensorflow_model(storage_client, load_transformer_example):
#     model, data = load_transformer_example
#     model_storage = TensorflowModelStorage(
#         artifact_type=ArtifactStorageType.TF_MODEL,
#         storage_client=storage_client,
#     )

#     uri = model_storage.save_artifact(
#         artifact=model,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )

#     loaded_model = model_storage.load_artifact(uri)
#     assert isinstance(loaded_model, type(model))


# @pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("s3_storage_client")])
# def test_parquet_cloud(test_arrow_table, storage_client, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset):
#     pq_writer = ParquetStorage(
#         storage_client=storage_client,
#         artifact_type=ArtifactStorageType.PYARROW,
#     )
#     uri = pq_writer.save_artifact(
#         artifact=test_arrow_table,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )

#     table = pq_writer.load_artifact(storage_uri=uri)
#     assert isinstance(table, pa.Table)


# @pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
# def test_parquet_local(test_arrow_table, storage_client):
#     pq_writer = ParquetStorage(
#         storage_client=storage_client,
#         artifact_type=ArtifactStorageType.PYARROW,
#     )
#     uri = pq_writer.save_artifact(
#         artifact=test_arrow_table,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )

#     table = pq_writer.load_artifact(storage_uri=uri)
#     assert isinstance(table, pa.Table)


# @pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
# def test_array(test_array, storage_client):
#     numpy_writer = NumpyStorage(
#         storage_client=storage_client,
#         artifact_type=ArtifactStorageType.NUMPY,
#     )
#     uri = numpy_writer.save_artifact(
#         artifact=test_array,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )

#     array = numpy_writer.load_artifact(storage_uri=uri)
#     assert isinstance(array, np.ndarray)


# @pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
# @pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
# def test_tensorflow_model(storage_client, load_transformer_example):
#     model, _ = load_transformer_example
#     model_storage = TensorflowModelStorage(
#         artifact_type=ArtifactStorageType.TF_MODEL,
#         storage_client=storage_client,
#     )

#     uri = model_storage.save_artifact(
#         artifact=model,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )
#     model = model_storage.load_artifact(storage_uri=uri)
#     assert model is not None


# @pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
# def test_pytorch_model(storage_client, load_pytorch_resnet):
#     model, data = load_pytorch_resnet
#     model_storage = PyTorchModelStorage(
#         artifact_type=ArtifactStorageType.PYTORCH,
#         storage_client=storage_client,
#     )

#     metadata = model_storage.save_artifact(
#         artifact=model,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )

#     model = model_storage.load_artifact(storage_uri=metadata)
#     assert model is not None


# def test_real_gcs_artifact(real_gcs: StorageClient, test_arrow_table) -> None:
#     pq_writer = ParquetStorage(
#         storage_client=real_gcs,
#         artifact_type=ArtifactStorageType.PYARROW,
#     )

#     uri = pq_writer.save_artifact(
#         artifact=test_arrow_table,
#         root_uri=conftest.save_path(),
#         filename="test",
#     )

#     table = pq_writer.load_artifact(uri)
#     assert isinstance(table, pa.Table)


# # @pytest.mark.skip(reason="Requires live GCS credentials")
# def test_real_gcs(tmp_path: Path, real_gcs: StorageClient, load_pytorch_resnet) -> None:
#     # create
#     #
#     # /tmp_path
#     #   /src
#     #     test1.txt
#     #     test2.txt
#     #   /dest
#     src_dir = tmp_path / "src"
#     src_dir.mkdir()
#     f = src_dir / "test.txt"
#     f.write_text("hello, world")
#     f2 = src_dir / "test2.txt"
#     f2.write_text("hello, again")

#     dest_dir = tmp_path / "dest"
#     dest_dir.mkdir()

#     print(tmp_path)
#     real_gcs.put(str(tmp_path) + "/", "some/really/nested/dir")

#     real_gcs.get("some/really/nested/dir", "/tmp/one", recursive=True)
#     real_gcs.get("some/really/nested/dir/", "/tmp/two", recursive=True)
#     real_gcs.get("some/really/nested/dir/src/test.txt", "/tmp/test.txt", recursive=False)
#     real_gcs.get("some/really/nested/dir/src", str(dest_dir), recursive=True)

#     assert Path(dest_dir).joinpath("test.txt").read_text() == "hello, world"
#     assert Path(dest_dir).joinpath("test2.txt").read_text() == "hello, again"

#     print(real_gcs.exists("some"))
#     print(real_gcs.exists("some/really"))
#     print(real_gcs.exists("some/really/nested/dir/src/test.txt"))
#     real_gcs.rm("some/really/nested/dir/src/test.txt")
#     real_gcs.rm("some")
