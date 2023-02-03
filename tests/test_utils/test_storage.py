import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from opsml_artifacts.registry.cards.storage import NumpyStorage, ParquetStorage, JoblibStorage, SaveInfo
from opsml_artifacts.drift.data_drift import DriftDetector


def test_parquet(test_arrow_table, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset):

    save_info = SaveInfo(
        blob_path="blob",
        version=1,
        team="mlops",
        name="test",
    )
    pq_writer = ParquetStorage(save_info=save_info)
    metadata = pq_writer.save_artifact(artifact=test_arrow_table)

    assert isinstance(metadata.uri, str)

    df = pq_writer.load_artifact(storage_uri=metadata.uri)
    assert isinstance(df, pd.DataFrame)


def test_array(test_array, mock_pyarrow_parquet_write):
    save_info = SaveInfo(
        blob_path="blob",
        version=1,
        team="mlops",
        name="test",
    )
    np_writer = NumpyStorage(save_info=save_info)
    metadata = np_writer.save_artifact(artifact=test_array)

    with patch("numpy.load", return_value=test_array):
        array = np_writer.load_artifact(storage_uri=metadata.uri)
        assert isinstance(array, np.ndarray)


@pytest.mark.parametrize("categorical", [["col_10"]])
def test_drift_storage(drift_dataframe, categorical):

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
        version=1,
        team="mlops",
        name="test",
    )

    with patch.multiple(
        "joblib",
        dump=MagicMock(return_value=None),
        load=MagicMock(return_value=drift_report),
    ):
        drift_writer = JoblibStorage(save_info=save_info)
        metadata = drift_writer.save_artifact(artifact=drift_report)

        drift_report = drift_writer.load_artifact(storage_uri=metadata.uri)
        assert isinstance(drift_report, dict)
