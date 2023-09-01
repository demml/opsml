import sys
import numpy as np
import pyarrow as pa
import pytest
import json
import os
from pytest_lazyfixture import lazy_fixture
from unittest.mock import patch, MagicMock
from opsml.registry.storage.artifact_storage import (
    ParquetStorage,
    NumpyStorage,
    TensorflowModelStorage,
    PyTorchModelStorage,
    JSONStorage,
)
import tempfile
from opsml.registry.storage.storage_system import LocalStorageClient
from opsml.helpers import utils
from opsml.registry.storage.types import ArtifactStorageSpecs

# from opsml.drift.data_drift import DriftDetector
from tests import conftest


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_parquet(test_arrow_table, storage_client):
    storage_spec = ArtifactStorageSpecs(save_path=conftest.save_path())

    storage_client.storage_spec = storage_spec
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type="Table",
    )
    metadata = pq_writer.save_artifact(artifact=test_arrow_table)

    assert isinstance(metadata.uri, str)

    table = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(table, pa.Table)


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_numpy(test_array, storage_client):
    storage_spec = ArtifactStorageSpecs(save_path=conftest.save_path())

    storage_client.storage_spec = storage_spec
    numpy_writer = NumpyStorage(
        storage_client=storage_client,
        artifact_type="ndarray",
    )
    metadata = numpy_writer.save_artifact(artifact=test_array)

    array = numpy_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(array, np.ndarray)


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_json(storage_client):
    storage_spec = ArtifactStorageSpecs(save_path=conftest.save_path())

    # Data to be written
    dictionary = {
        "id": "04",
        "name": "test",
    }

    # Serializing json
    json_object = json.dumps(dictionary, indent=4)
    storage_client.storage_spec = storage_spec

    json_writer = JSONStorage(
        artifact_type="json",
        storage_client=storage_client,
    )
    metadata = json_writer.save_artifact(artifact=json_object)

    loaded_json = json_writer.load_artifact(storage_uri=metadata.uri)

    assert loaded_json == dictionary


@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_pytorch_model(storage_client, load_pytorch_resnet):
    model, data = load_pytorch_resnet
    storage_spec = ArtifactStorageSpecs(save_path=conftest.save_path())

    storage_client.storage_spec = storage_spec
    model_storage = PyTorchModelStorage(
        artifact_type="pytorch",
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(artifact=model)

    model = model_storage.load_artifact(storage_uri=metadata.uri)

    assert model == model


@pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on apple silicon")
@pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_tensorflow_model(storage_client, load_transformer_example):
    model, data = load_transformer_example
    storage_spec = ArtifactStorageSpecs(save_path=conftest.save_path())

    storage_client.storage_spec = storage_spec
    model_storage = TensorflowModelStorage(
        artifact_type="keras",
        storage_client=storage_client,
    )

    metadata = model_storage.save_artifact(artifact=model)

    model = model_storage.load_artifact(storage_uri=metadata.uri)

    assert model == model


@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client")])
def test_parquet_gcs(test_arrow_table, storage_client, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset):
    storage_spec = ArtifactStorageSpecs(save_path="blob")

    storage_client.storage_spec = storage_spec
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type="Table",
    )
    metadata = pq_writer.save_artifact(artifact=test_arrow_table)
    assert isinstance(metadata.uri, str)

    table = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(table, pa.Table)

    storage_client.list_files(metadata.uri)
    storage_client.delete(metadata.uri)


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_parquet_local(test_arrow_table, storage_client, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset):
    storage_spec = ArtifactStorageSpecs(save_path="blob")

    storage_client.storage_spec = storage_spec
    pq_writer = ParquetStorage(
        storage_client=storage_client,
        artifact_type="Table",
    )
    metadata = pq_writer.save_artifact(artifact=test_arrow_table)
    assert isinstance(metadata.uri, str)

    table = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(table, pa.Table)


@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_array(test_array, storage_client, mock_pyarrow_parquet_write):
    storage_spec = ArtifactStorageSpecs(save_path="blob")

    storage_client.storage_spec = storage_spec
    with patch.multiple(
        "zarr",
        save=MagicMock(return_value=None),
        load=MagicMock(return_value=test_array),
    ):
        numpy_writer = NumpyStorage(
            storage_client=storage_client,
            artifact_type="ndarray",
        )
        metadata = numpy_writer.save_artifact(artifact=test_array)

        array = numpy_writer.load_artifact(storage_uri=metadata.uri)
        assert isinstance(array, np.ndarray)


@pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on apple silicon")
@pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_tensorflow_model(storage_client, load_transformer_example, mock_pathlib):
    model, data = load_transformer_example
    storage_spec = ArtifactStorageSpecs(save_path="blob")

    storage_client.storage_spec = storage_spec
    model_storage = TensorflowModelStorage(
        artifact_type="keras",
        storage_client=storage_client,
    )

    with patch.multiple(
        "tensorflow.keras.Model",
        save=MagicMock(return_value=None),
    ):
        metadata = model_storage.save_artifact(artifact=model)

    with patch.multiple(
        "tensorflow.keras.models",
        load_model=MagicMock(return_value=model),
    ):
        model = model_storage.load_artifact(storage_uri=metadata.uri)


@pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on apple silicon")
@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_pytorch_model(storage_client, load_pytorch_resnet, mock_pathlib):
    model, data = load_pytorch_resnet
    storage_spec = ArtifactStorageSpecs(save_path="blob")

    storage_client.storage_spec = storage_spec
    model_storage = PyTorchModelStorage(
        artifact_type="pytorch",
        storage_client=storage_client,
    )

    with patch.multiple(
        "torch",
        save=MagicMock(return_value=None),
    ):
        metadata = model_storage.save_artifact(artifact=model)

    with patch.multiple(
        "torch",
        load=MagicMock(return_value=model),
    ):
        model = model_storage.load_artifact(storage_uri=metadata.uri)


@pytest.mark.parametrize("storage_client", [lazy_fixture("local_storage_client")])
def test_local_paths(storage_client: LocalStorageClient):
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
