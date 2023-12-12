import json
import os
import sys
import tempfile

import numpy as np
import pyarrow as pa
import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.helpers import utils
from opsml.registry.storage.artifact_storage import (
    JSONStorage,
    NumpyStorage,
    ParquetStorage,
    PyTorchModelStorage,
    TensorflowModelStorage,
)
from opsml.registry.storage.storage_system import StorageClient
from opsml.registry.storage.types import ArtifactStorageSpecs
from tests import conftest


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_parquet(test_arrow_table, storage_client):
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type="Table",
    )

    metadata = pq_writer.save_artifact(
        artifact=test_arrow_table,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )

    assert isinstance(metadata.uri, str)

    table = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(table, pa.Table)


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_api_numpy(test_array, storage_client):
    numpy_writer = NumpyStorage(
        storage_client=storage_client,
        artifact_type="ndarray",
    )
    metadata = numpy_writer.save_artifact(
        artifact=test_array,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )

    array = numpy_writer.load_artifact(storage_uri=metadata.uri)
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
        artifact_type="json",
        storage_client=storage_client,
    )
    metadata = json_writer.save_artifact(
        artifact=json_object,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )

    loaded_json = json_writer.load_artifact(storage_uri=metadata.uri)

    assert loaded_json == dictionary


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_pytorch_model(storage_client, load_pytorch_resnet):
    model, data = load_pytorch_resnet

    model_storage = PyTorchModelStorage(
        artifact_type="pytorch",
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(
        artifact=model,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )

    model = model_storage.load_artifact(storage_uri=metadata.uri)

    assert model == model


@pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_tensorflow_model(storage_client, load_transformer_example):
    model, data = load_transformer_example
    model_storage = TensorflowModelStorage(
        artifact_type="keras",
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(
        artifact=model,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )

    model = model_storage.load_artifact(storage_uri=metadata.uri)

    assert model == model


@pytest.mark.parametrize(
    "storage_client",
    [lazy_fixture("gcp_storage_client"), lazy_fixture("s3_storage_client")],
)
def test_parquet_cloud(test_arrow_table, storage_client, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset):
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type="Table",
    )
    metadata = pq_writer.save_artifact(
        artifact=test_arrow_table,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )
    assert isinstance(metadata.uri, str)

    table = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(table, pa.Table)

    storage_client.list_files(metadata.uri)
    storage_client.delete(metadata.uri)


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_parquet_local(test_arrow_table, storage_client):
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type="Table",
    )
    metadata = pq_writer.save_artifact(
        artifact=test_arrow_table,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path(), filename="test"),
    )
    assert isinstance(metadata.uri, str)

    table = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(table, pa.Table)


@pytest.mark.parametrize(
    "storage_client",
    [lazy_fixture("local_storage_client")],
)
def test_array(test_array, storage_client):
    numpy_writer = NumpyStorage(
        storage_client=storage_client,
        artifact_type="ndarray",
    )
    metadata = numpy_writer.save_artifact(
        artifact=test_array,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )

    array = numpy_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(array, np.ndarray)


@pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_tensorflow_model(storage_client, load_transformer_example):
    model, _ = load_transformer_example
    model_storage = TensorflowModelStorage(
        artifact_type="keras",
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(
        artifact=model,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )
    model = model_storage.load_artifact(storage_uri=metadata.uri)
    assert model is not None


@pytest.mark.parametrize(
    "storage_client",
    [lazy_fixture("local_storage_client")],
)
def test_pytorch_model(storage_client, load_pytorch_resnet):
    model, data = load_pytorch_resnet
    model_storage = PyTorchModelStorage(
        artifact_type="pytorch",
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(
        artifact=model,
        storage_spec=ArtifactStorageSpecs(save_path=conftest.save_path()),
    )

    model = model_storage.load_artifact(storage_uri=metadata.uri)
    assert model is not None


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_local_paths(storage_client: StorageClient):
    FILENAME = "example.csv"
    file_path = utils.FindPath.find_filepath(name=FILENAME)

    with tempfile.TemporaryDirectory() as tempdir:
        storage_client.upload(local_path=file_path, write_path=f"{tempdir}/{FILENAME}")

        dir_path = utils.FindPath.find_dirpath(
            anchor_file=FILENAME,
            dir_name="assets",
            path=os.getcwd(),
        )

        storage_client.upload(local_path=dir_path, write_path=f"{tempdir}/assets")


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_create_temp_save_path(storage_client: StorageClient) -> None:
    s = ArtifactStorageSpecs(save_path="dir", filename="test.txt")
    with storage_client.create_temp_save_path_with_spec(s) as (storage_uri, local_path):
        assert storage_uri == os.path.join(storage_client.base_path_prefix, "dir", "test.txt")
        assert not os.path.exists(local_path)
        assert os.path.basename(local_path) == "test.txt"
