import numpy as np
import pandas as pd
import pyarrow as pa
import pytest
from pytest_lazyfixture import lazy_fixture
from unittest.mock import patch, MagicMock
from opsml_artifacts.registry.cards.artifact_storage import (
    ParquetStorage,
    JoblibStorage,
    SaveInfo,
    NumpyStorage,
    TensorflowModelStorage,
    PyTorchModelStorage,
)
from opsml_artifacts.drift.data_drift import DriftDetector


@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_parquet_gcs(test_arrow_table, storage_client, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset):

    save_info = SaveInfo(
        blob_path="blob",
        version="1.0.0",
        team="mlops",
        name="test",
    )
    pq_writer = ParquetStorage(
        save_info=save_info,
        storage_client=storage_client,
        artifact_type="Table",
    )
    metadata = pq_writer.save_artifact(artifact=test_arrow_table)

    assert isinstance(metadata.uri, str)

    table = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(table, pa.Table)


@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_array(test_array, storage_client, mock_pyarrow_parquet_write):
    save_info = SaveInfo(
        blob_path="blob",
        version="1.0.0",
        team="mlops",
        name="test",
    )

    with patch.multiple(
        "zarr",
        save=MagicMock(return_value=None),
        load=MagicMock(return_value=test_array),
    ):
        numpy_writer = NumpyStorage(
            save_info=save_info,
            storage_client=storage_client,
            artifact_type="ndarray",
        )
        metadata = numpy_writer.save_artifact(artifact=test_array)

        array = numpy_writer.load_artifact(storage_uri=metadata.uri)
        assert isinstance(array, np.ndarray)


@pytest.mark.parametrize("categorical", [["col_10"]])
@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_drift_storage(drift_dataframe, categorical, storage_client):

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

    save_info = SaveInfo(
        blob_path="blob",
        version="1.0.0",
        team="mlops",
        name="test",
    )

    with patch.multiple(
        "joblib",
        dump=MagicMock(return_value=None),
        load=MagicMock(return_value=drift_report),
    ):
        drift_writer = JoblibStorage(
            save_info=save_info,
            storage_client=storage_client,
            artifact_type="joblib",
        )
        metadata = drift_writer.save_artifact(artifact=drift_report)

        drift_report = drift_writer.load_artifact(storage_uri=metadata.uri)
        assert isinstance(drift_report, dict)


@pytest.mark.parametrize("storage_client", [lazy_fixture("gcp_storage_client"), lazy_fixture("local_storage_client")])
def test_tensorflow_model(storage_client, load_transformer_example):
    model, data = load_transformer_example
    save_info = SaveInfo(
        blob_path="blob",
        version="1.0.0",
        team="mlops",
        name="test",
    )

    model_storage = TensorflowModelStorage(
        artifact_type="keras",
        save_info=save_info,
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
def test_pytorch_model(storage_client, load_pytorch_resnet):
    model, data = load_pytorch_resnet
    save_info = SaveInfo(
        blob_path="blob",
        version="1.0.0",
        team="mlops",
        name="test",
    )

    model_storage = PyTorchModelStorage(
        artifact_type="pytorch",
        save_info=save_info,
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
