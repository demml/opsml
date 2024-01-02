import json

import numpy as np
import pyarrow as pa
import pytest

from opsml.registry.storage.artifact import (
    ArtifactStorageType,
    JSONStorage,
    NumpyStorage,
    ParquetStorage,
)
from opsml.registry.storage.client import StorageClient
from tests import conftest

pytestmark = pytest.mark.skip(reason="Requires live GCS credentials")


def test_gcs_parquet(real_gcs: StorageClient, test_arrow_table) -> None:
    pq_writer = ParquetStorage(
        storage_client=real_gcs,
        artifact_type=ArtifactStorageType.PYARROW,
    )

    uri = pq_writer.save_artifact(
        artifact=test_arrow_table,
        root_uri=conftest.save_path(),
        filename="test",
    )

    table = pq_writer.load_artifact(uri)
    assert isinstance(table, pa.Table)


def test_gcs_numpy(real_gcs: StorageClient, test_array):
    numpy_writer = NumpyStorage(
        storage_client=real_gcs,
        artifact_type=ArtifactStorageType.NUMPY,
    )
    uri = numpy_writer.save_artifact(
        artifact=test_array,
        root_uri=conftest.save_path(),
        filename="test",
    )

    array = numpy_writer.load_artifact(storage_uri=uri)
    assert isinstance(array, np.ndarray)


def test_gcs_json(real_gcs: StorageClient):
    # Data to be written
    dictionary = {
        "id": "04",
        "name": "test",
    }

    # Serializing json
    json_object = json.dumps(dictionary, indent=4)

    json_writer = JSONStorage(
        artifact_type=ArtifactStorageType.JSON,
        storage_client=real_gcs,
    )
    uri = json_writer.save_artifact(
        artifact=json_object,
        root_uri=conftest.save_path(),
        filename="test",
    )

    loaded_json = json_writer.load_artifact(storage_uri=uri)

    assert loaded_json == dictionary
