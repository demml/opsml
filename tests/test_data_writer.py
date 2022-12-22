from opsml_data.registry.data_writer import ParquetWriter, NumpyWriter
import pandas as pd
import numpy as np


def test_parquet(test_arrow_table, storage_client):
    pq_wrtier = ParquetWriter()
    metadata = pq_wrtier.save_data(
        data=test_arrow_table,
        data_name="pq_test",
        version=1,
        team="mlops",
    )

    assert isinstance(metadata.gcs_uri, str)

    df = pq_wrtier.load_data(storage_uri=metadata.gcs_uri)
    assert isinstance(df, pd.DataFrame)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)


def test_array(test_array, storage_client):
    np_writer = NumpyWriter()

    metadata = np_writer.save_data(
        data=test_array,
        data_name="pq_test",
        version=1,
        team="mlops",
    )

    array = np_writer.load_data(storage_uri=metadata.gcs_uri)
    assert isinstance(array, np.ndarray)

    storage_client.delete_object_from_url(gcs_uri=metadata.gcs_uri)
