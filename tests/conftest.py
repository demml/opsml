import os
import pytest

import requests

#
## from opsml_artifacts.helpers.settings import SnowflakeParams
from opsml_artifacts.registry.sql.sql_schema import DataSchema, ModelSchema, ExperimentSchema, PipelineSchema
from opsml_artifacts.registry.sql.registry import CardRegistry
from opsml_artifacts.helpers.gcp_utils import GCPMLScheduler, GCSStorageClient, GcpCreds
from opsml_artifacts.helpers.models import StorageClientSettings, GcsStorageClientSettings
from opsml_artifacts.registry.cards.storage_system import StorageClientGetter
from opsml_artifacts.registry.sql.connectors.connector import LocalSQLConnection
from opsml_artifacts.helpers.request_helpers import ApiClient
from opsml_artifacts.registry.sql.registry_base import SQLRegistryAPI
from opsml_artifacts.scripts.load_model_card import ModelLoaderCli
from opsml_artifacts.registry.model.types import ModelApiDef
from opsml_artifacts import ModelCard
from google.auth import load_credentials_from_file
from unittest.mock import patch, MagicMock

from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.ensemble import StackingRegressor
import lightgbm as lgb
import numpy as np
import pandas as pd
import pyarrow as pa
from pydantic import BaseModel

session = requests.Session()

################ Test Classes
class Blob(BaseModel):
    name: str = "test_upload/test.csv"

    def download_to_filename(self, destination_filename):
        return True

    def upload_from_filename(self, filename):
        return True

    def delete(self):
        return True


class Bucket(BaseModel):
    name: str = "bucket"

    def blob(self, path: str):
        return Blob()

    def list_blobs(self, prefix: str):
        return [Blob()]


@pytest.fixture(scope="function")
def mock_gcp_vars():
    cred_path = os.path.join(os.path.dirname(__file__), "assets/fake_gcp_creds.json")
    creds, _ = load_credentials_from_file(cred_path)
    mock_vars = {
        "gcp_project": "test",
        "gcs_bucket": "test",
        "gcp_region": "test",
        "app_env": "staging",
        "path": os.getcwd(),
        "gcp_creds": creds,
        "gcsfs_creds": creds,
    }
    return mock_vars


@pytest.fixture(scope="function")
def mock_gcp_creds(mock_gcp_vars):

    creds = GcpCreds(
        creds=mock_gcp_vars["gcp_creds"],
        project=mock_gcp_vars["gcp_project"],
    )

    with patch.multiple(
        "opsml_artifacts.helpers.gcp_utils.GcpCredsSetter",
        get_creds=MagicMock(return_value=creds),
    ) as mock_gcp_creds:

        yield mock_gcp_creds


@pytest.fixture(scope="function")
def gcp_storage_client(mock_gcp_vars):
    gcs_info = GcsStorageClientSettings(
        storage_type="gcs",
        storage_uri="gs://test",
        credentials=mock_gcp_vars["gcp_creds"],
        gcp_project=mock_gcp_vars["gcp_project"],
    )
    storage_client = StorageClientGetter.get_storage_client(storage_info=gcs_info)
    return storage_client


@pytest.fixture(scope="function")
def local_storage_client():

    storage_client = StorageClientGetter.get_storage_client(storage_info=StorageClientSettings())
    return storage_client


@pytest.fixture(scope="session", autouse=True)
def mock_gcsfs():
    with patch.multiple(
        "gcsfs.GCSFileSystem",
        ls=MagicMock(return_value=["gs://test"]),
        upload=MagicMock(return_value=True),
        download=MagicMock(return_value=True),
    ) as mocked_gcsfs:
        yield mocked_gcsfs


@pytest.fixture(scope="session", autouse=True)
def mock_pathlib():
    with patch.multiple("pathlib.Path", mkdir=MagicMock(return_value=None)) as mocked_pathlib:
        yield mocked_pathlib


@pytest.fixture(scope="function")
def mock_joblib_storage():
    with patch.multiple(
        "opsml_artifacts.registry.cards.artifact_storage.JoblibStorage",
        _save_json=MagicMock(return_value=None),
        _save_joblib=MagicMock(return_value=None),
        _load_joblib=MagicMock(return_value=None),
        _load_json=MagicMock(return_value=None),
    ) as mocked_joblib:
        yield mocked_joblib


@pytest.fixture(scope="function")
def mock_pyarrow_parquet_write():
    with patch.multiple("pyarrow.parquet", write_table=MagicMock(return_value=True)) as mock_:
        yield mock_


@pytest.fixture(scope="function")
def mock_pyarrow_parquet_dataset(test_df, test_arrow_table):
    with patch("pyarrow.parquet.ParquetDataset") as mock_:
        mock_dataset = mock_.return_value
        mock_dataset.read.return_value = test_arrow_table
        mock_dataset.read.to_pandas.return_value = test_df

        yield mock_dataset


######### Data for registry tests
@pytest.fixture(scope="function")
def test_array():
    data = np.random.rand(10, 100)
    return data


@pytest.fixture(scope="function")
def test_split_array():
    indices = np.array([0, 1, 2])
    return [{"label": "train", "indices": indices}]


@pytest.fixture(scope="function")
def test_df():
    df = pd.DataFrame(
        {
            "year": [2020, 2022, 2019, 2021],
            "n_legs": [2, 4, 5, 100],
            "animals": ["Flamingo", "Horse", "Brittle stars", "Centipede"],
        }
    )
    return df


@pytest.fixture(scope="session")
def test_arrow_table():
    n_legs = pa.array([2, 4, 5, 100])
    animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
    names = ["n_legs", "animals"]
    table = pa.Table.from_arrays([n_legs, animals], names=names)
    return table


@pytest.fixture(scope="function")
def drift_dataframe():
    mu_1 = -4  # mean of the first distribution
    mu_2 = 4  # mean of the second distribution
    X_train = np.random.normal(mu_1, 2.0, size=(1000, 10))
    cat = np.random.randint(0, 3, 1000).reshape(-1, 1)
    X_train = np.hstack((X_train, cat))
    X_test = np.random.normal(mu_2, 2.0, size=(1000, 10))
    cat = np.random.randint(2, 5, 1000).reshape(-1, 1)
    X_test = np.hstack((X_test, cat))
    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")
    X_train = pd.DataFrame(X_train, columns=col_names)
    X_test = pd.DataFrame(X_test, columns=col_names)
    y_train = np.random.randint(1, 10, size=(1000, 1))
    y_test = np.random.randint(1, 10, size=(1000, 1))
    return X_train, y_train, X_test, y_test


#################################### MODELS ###################################
@pytest.fixture(scope="module")
def linear_regression():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    reg = LinearRegression().fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def sklearn_pipeline():
    data = pd.DataFrame(
        [
            dict(CAT1="a", CAT2="c", num1=0.5, num2=0.6, num3=0, y=0),
            dict(CAT1="b", CAT2="d", num1=0.4, num2=0.8, num3=1, y=1),
            dict(CAT1="a", CAT2="d", num1=0.5, num2=0.56, num3=0, y=0),
            dict(CAT1="a", CAT2="d", num1=0.55, num2=0.56, num3=2, y=1),
            dict(CAT1="a", CAT2="c", num1=0.35, num2=0.86, num3=0, y=0),
            dict(CAT1="a", CAT2="c", num1=0.5, num2=0.68, num3=2, y=1),
        ]
    )
    cat_cols = ["CAT1", "CAT2"]
    train_data = data.drop("y", axis=1)
    categorical_transformer = Pipeline([("onehot", OneHotEncoder(sparse=False, handle_unknown="ignore"))])
    preprocessor = ColumnTransformer(
        transformers=[("cat", categorical_transformer, cat_cols)],
        remainder="passthrough",
    )
    pipe = Pipeline([("preprocess", preprocessor), ("rf", lgb.LGBMRegressor())])
    pipe.fit(train_data, data["y"])
    return pipe, train_data


@pytest.fixture(scope="function")
def test_model_card(sklearn_pipeline):
    # create data card
    model, data = sklearn_pipeline
    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
    )
    return model_card
