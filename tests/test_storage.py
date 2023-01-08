import numpy as np
import pandas as pd
import pytest
from opsml_data.registry.storage import NumpyStorage, ParquetStorage, DriftStorage, DataSaveInfo
from opsml_data.drift.data_drift import DriftDetector


def test_parquet(test_arrow_table, storage_client):

    save_info = DataSaveInfo(
        blob_path="blob",
        version=1,
        team="mlops",
        data_name="test",
    )
    pq_wrtier = ParquetStorage(save_info=save_info)
    metadata = pq_wrtier.save_data(data=test_arrow_table)

    assert isinstance(metadata.gcs_uri, str)

    df = pq_wrtier.load_data(storage_uri=metadata.gcs_uri)
    assert isinstance(df, pd.DataFrame)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)


def test_array(test_array, storage_client):
    save_info = DataSaveInfo(
        blob_path="blob",
        version=1,
        team="mlops",
        data_name="test",
    )
    np_writer = NumpyStorage(save_info=save_info)
    metadata = np_writer.save_data(data=test_array)

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

    save_info = DataSaveInfo(
        blob_path="blob",
        version=1,
        team="mlops",
        data_name="test",
    )

    drift_writer = DriftStorage(save_info=save_info)
    metadata = drift_writer.save_data(data=drift_report)

    drift_report = drift_writer.load_data(storage_uri=metadata.gcs_uri)
    assert isinstance(drift_report, dict)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)
