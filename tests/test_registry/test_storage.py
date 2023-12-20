import json
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.registry.storage.artifact import (
    ArtifactStorageType,
    JSONStorage,
    NumpyStorage,
    ParquetStorage,
    PyTorchModelStorage,
    TensorflowModelStorage,
)
from opsml.registry.storage.client import StorageClient
from tests import conftest


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_parquet(test_arrow_table, storage_client):
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type=ArtifactStorageType.PYARROW,
    )

    uri = pq_writer.save_artifact(
        artifact=test_arrow_table,
        root_uri=conftest.save_path(),
        filename="test",
    )

    table = pq_writer.load_artifact(uri)
    assert isinstance(table, pa.Table)


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_api_numpy(test_array, storage_client):
    numpy_writer = NumpyStorage(
        storage_client=storage_client,
        artifact_type=ArtifactStorageType.NUMPY,
    )
    uri = numpy_writer.save_artifact(
        artifact=test_array,
        root_uri=conftest.save_path(),
        filename="test",
    )

    array = numpy_writer.load_artifact(storage_uri=uri)
    assert isinstance(array, np.ndarray)


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_json(storage_client):
    # Data to be written
    dictionary = {
        "id": "04",
        "name": "test",
    }

    # Serializing json
    json_object = json.dumps(dictionary, indent=4)

    json_writer = JSONStorage(
        artifact_type=ArtifactStorageType.JSON,
        storage_client=storage_client,
    )
    uri = json_writer.save_artifact(
        artifact=json_object,
        root_uri=conftest.save_path(),
        filename="test",
    )

    loaded_json = json_writer.load_artifact(storage_uri=uri)

    assert loaded_json == dictionary


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_pytorch_model(storage_client, load_pytorch_resnet):
    model, data = load_pytorch_resnet

    model_storage = PyTorchModelStorage(
        artifact_type=ArtifactStorageType.PYTORCH,
        storage_client=storage_client,
    )

    uri = model_storage.save_artifact(
        artifact=model,
        root_uri=conftest.save_path(),
        filename="test",
    )

    loaded_model = model_storage.load_artifact(storage_uri=uri)
    assert isinstance(loaded_model, type(model))


@pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_tensorflow_model(storage_client, load_transformer_example):
    model, data = load_transformer_example
    model_storage = TensorflowModelStorage(
        artifact_type=ArtifactStorageType.TF_MODEL,
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(
        artifact=model,
        root_uri=conftest.save_path(),
        filename="test",
    )

    loaded_model = model_storage.load_artifact(storage_uri=metadata)
    assert isinstance(loaded_model, type(model))


@pytest.mark.parametrize(
    "storage_client",
    [lazy_fixture("gcp_storage_client"), lazy_fixture("s3_storage_client")],
)
def test_parquet_cloud(
    test_arrow_table, storage_client, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset, mock_gcp_creds
):
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type=ArtifactStorageType.PYARROW,
    )
    uri = pq_writer.save_artifact(
        artifact=test_arrow_table,
        root_uri=conftest.save_path(),
        filename="test",
    )

    table = pq_writer.load_artifact(storage_uri=uri)
    assert isinstance(table, pa.Table)

    storage_client.list_files(uri)
    storage_client.delete(uri)


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_parquet_local(test_arrow_table, storage_client):
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type=ArtifactStorageType.PYARROW,
    )
    uri = pq_writer.save_artifact(
        artifact=test_arrow_table,
        root_uri=conftest.save_path(),
        filename="test",
    )

    table = pq_writer.load_artifact(storage_uri=uri)
    assert isinstance(table, pa.Table)


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_array(test_array, storage_client):
    numpy_writer = NumpyStorage(
        storage_client=storage_client,
        artifact_type=ArtifactStorageType.NUMPY,
    )
    uri = numpy_writer.save_artifact(
        artifact=test_array,
        root_uri=conftest.save_path(),
        filename="test",
    )

    array = numpy_writer.load_artifact(storage_uri=uri)
    assert isinstance(array, np.ndarray)


@pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_tensorflow_model(storage_client, load_transformer_example):
    model, _ = load_transformer_example
    model_storage = TensorflowModelStorage(
        artifact_type=ArtifactStorageType.TF_MODEL,
        storage_client=storage_client,
    )

    uri = model_storage.save_artifact(
        artifact=model,
        root_uri=conftest.save_path(),
        filename="test",
    )
    model = model_storage.load_artifact(storage_uri=uri)
    assert model is not None


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_pytorch_model(storage_client, load_pytorch_resnet):
    model, data = load_pytorch_resnet
    model_storage = PyTorchModelStorage(
        artifact_type=ArtifactStorageType.PYTORCH,
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(
        artifact=model,
        root_uri=conftest.save_path(),
        filename="test",
    )

    model = model_storage.load_artifact(storage_uri=metadata)
    assert model is not None


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_create_temp_save_path(storage_client: StorageClient) -> None:
    with storage_client.create_tmp_path("/some/long/path/with/file.txt") as tmp_path:
        tmp_path = Path(tmp_path)
        assert tmp_path.parent.exists() and tmp_path.parent.is_dir() and tmp_path.name == "file.txt"
