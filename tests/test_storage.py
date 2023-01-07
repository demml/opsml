import numpy as np
import pandas as pd
import pytest
from opsml_data.registry.storage import NumpyStorage, ParquetStorage, DriftStorage
from opsml_data.drift.data_drift import DriftDetector


def test_parquet(test_arrow_table, storage_client):
    pq_wrtier = ParquetStorage()  # change this to bucket name
    metadata = pq_wrtier.save_data(
        data=test_arrow_table,
        data_name="pq_test",
        version=1,
        blob_path="blob",
        team="mlops",
    )

    assert isinstance(metadata.gcs_uri, str)

    df = pq_wrtier.load_data(storage_uri=metadata.gcs_uri)
    assert isinstance(df, pd.DataFrame)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)


def test_array(test_array, storage_client):
    np_writer = NumpyStorage()

    metadata = np_writer.save_data(
        data=test_array,
        data_name="pq_test",
        version=1,
        blob_path="blob",
        team="mlops",
    )

    array = np_writer.load_data(storage_uri=metadata.gcs_uri)
    assert isinstance(array, np.ndarray)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)


@pytest.mark.parametrize("categorical", [["col_10"]])
def test_drift_storage(drift_dataframe, categorical, storage_client):

    X_train, y_train, X_test, y_test = drift_dataframe

    detector = DriftDetector(
        x_reference=X_train,
        y_reference=y_train,
        x_current=X_test,
        y_current=y_test,
        target_feature_name="target",
        categorical_features=categorical,
    )

    drift_report = detector.run_drift_diagnostics(return_dataframe=False)
    drift_writer = DriftStorage()

    metadata = drift_writer.save_data(
        data=drift_report,
        data_name="drift_report",
        version=1,
        blob_path="blob",
        team="mlops",
    )

    drift_report = drift_writer.load_data(storage_uri=metadata.gcs_uri)
    assert isinstance(drift_report, dict)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)
