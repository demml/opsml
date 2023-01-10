import numpy as np
import pandas as pd
import pytest
from opsml_artifacts.registry.cards.storage import NumpyStorage, ParquetStorage, DictionaryStorage, SaveInfo
from opsml_artifacts.drift.data_drift import DriftDetector


def test_parquet(test_arrow_table, storage_client):

    save_info = SaveInfo(
        blob_path="blob",
        version=1,
        team="mlops",
        name="test",
    )
    pq_wrtier = ParquetStorage(save_info=save_info)
    metadata = pq_wrtier.save_artifact(artifact=test_arrow_table)

    assert isinstance(metadata.gcs_uri, str)

    df = pq_wrtier.load_artifact(storage_uri=metadata.gcs_uri)
    assert isinstance(df, pd.DataFrame)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)


def test_array(test_array, storage_client):
    save_info = SaveInfo(
        blob_path="blob",
        version=1,
        team="mlops",
        name="test",
    )
    np_writer = NumpyStorage(save_info=save_info)
    metadata = np_writer.save_artifact(artifact=test_array)

    array = np_writer.load_artifact(storage_uri=metadata.gcs_uri)
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

    drift_writer = DictionaryStorage(save_info=save_info)
    metadata = drift_writer.save_artifact(artifact=drift_report)

    drift_report = drift_writer.load_artifact(storage_uri=metadata.gcs_uri)
    assert isinstance(drift_report, dict)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)
