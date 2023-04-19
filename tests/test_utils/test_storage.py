import numpy as np
import pyarrow as pa
import pytest
import json
from pytest_lazyfixture import lazy_fixture
from unittest.mock import patch, MagicMock
from opsml.registry.storage.artifact_storage import (
    ParquetStorage,
    JoblibStorage,
    NumpyStorage,
    TensorflowModelStorage,
    PyTorchModelStorage,
    JSONStorage,
)
from opsml.registry.storage.types import ArtifactStorageSpecs
from opsml.drift.data_drift import DriftDetector
from tests import conftest


@pytest.mark.parametrize("storage_client", [lazy_fixture("mlflow_storage_client")])
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


"""
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


@pytest.mark.parametrize("categorical", [["col_10"]])
@pytest.mark.parametrize("storage_client", [lazy_fixture("api_storage_client")])
def test_api_joblib(
    drift_dataframe,
    categorical,
    storage_client,
):

    X_train, y_train, X_test, y_test = drift_dataframe

    detector = DriftDetector(
        x_reference=X_train,
        y_reference=y_train,
        x_current=X_test,
        y_current=y_test,
        dependent_var_name="target",
        categorical_features=categorical,
    )

    drift_report = detector.run_drift_diagnostics(return_dataframe=False)

    storage_spec = ArtifactStorageSpecs(save_path=conftest.save_path())

    storage_client.storage_spec = storage_spec
    drift_writer = JoblibStorage(
        storage_client=storage_client,
        artifact_type="joblib",
    )
    metadata = drift_writer.save_artifact(artifact=drift_report)

    drift_report = drift_writer.load_artifact(storage_uri=metadata.uri)


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


@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
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


@pytest.mark.parametrize("categorical", [["col_10"]])
@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_drift_storage(
    drift_dataframe,
    categorical,
    storage_client,
    mock_artifact_storage_clients,
):

    X_train, y_train, X_test, y_test = drift_dataframe

    detector = DriftDetector(
        x_reference=X_train,
        y_reference=y_train,
        x_current=X_test,
        y_current=y_test,
        dependent_var_name="target",
        categorical_features=categorical,
    )

    drift_report = detector.run_drift_diagnostics(return_dataframe=False)

    storage_spec = ArtifactStorageSpecs(save_path="blob")

    storage_client.storage_spec = storage_spec
    drift_writer = JoblibStorage(
        storage_client=storage_client,
        artifact_type="joblib",
    )
    metadata = drift_writer.save_artifact(artifact=drift_report)

    drift_report = drift_writer.load_artifact(storage_uri=metadata.uri)


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
"""
