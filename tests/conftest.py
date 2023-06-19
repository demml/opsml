from typing import Any, Iterator, Optional, Union
from dataclasses import dataclass
import os
import pathlib

# setting initial env vars to override default sql db
# these must be set prior to importing opsml since they establish their
DB_FILE_PATH = str(pathlib.Path.home().joinpath("tmp.db"))
SQL_PATH = f"sqlite:///{DB_FILE_PATH}"
STORAGE_PATH = str(pathlib.Path.home().joinpath("mlruns"))

os.environ["APP_ENV"] = "production"
os.environ["OPSML_PROD_TOKEN"] = "test-token"
os.environ["OPSML_TRACKING_URI"] = SQL_PATH
os.environ["OPSML_STORAGE_URI"] = STORAGE_PATH
os.environ["OPSML_USERNAME"] = "test-user"
os.environ["OPSML_PASSWORD"] = "test-pass"
os.environ["_MLFLOW_SERVER_ARTIFACT_DESTINATION"] = STORAGE_PATH
os.environ["_MLFLOW_SERVER_ARTIFACT_ROOT"] = "mlflow-artifacts:/"
os.environ["_MLFLOW_SERVER_FILE_STORE"] = SQL_PATH
os.environ["_MLFLOW_SERVER_SERVE_ARTIFACTS"] = "true"

import uuid
import pytest
import shutil
import httpx
from google.auth import load_credentials_from_file
from unittest.mock import patch, MagicMock, PropertyMock
from starlette.testclient import TestClient
import time
import datetime
import tempfile

import pyarrow as pa
from pydantic import BaseModel

import numpy as np
import joblib
import pandas as pd
import polars as pl

# ml model packages and classes
from sklearn.datasets import fetch_openml
from sklearn import (
    linear_model,
    tree,
    naive_bayes,
    gaussian_process,
    neighbors,
    svm,
    multioutput,
    multiclass,
    neural_network,
    cross_decomposition,
)
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.datasets import load_iris
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn import ensemble
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import lightgbm as lgb


# opsml
from opsml.registry.data.splitter import DataSplit
from opsml.registry.cards.types import ModelCardUris
from opsml.registry import ModelCard
from opsml.helpers.gcp_utils import GcpCreds, GCSStorageClient
from opsml.registry.storage.types import StorageClientSettings, GcsStorageClientSettings
from opsml.registry.sql.sql_schema import BaseMixin, Base, DBInitializer
from opsml.registry.sql.connectors.connector import LocalSQLConnection
from opsml.registry.storage.storage_system import StorageClientGetter, StorageSystem
from opsml.projects import get_project
from opsml.projects.mlflow import MlflowProject
from opsml.projects.base.types import ProjectInfo
from opsml.registry import CardRegistries
from opsml.projects import OpsmlProject
from opsml.model.types import OnnxModelDefinition


# testing
from tests.mock_api_registries import CardRegistry as ClientCardRegistry

CWD = os.getcwd()
fourteen_days_ago = datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(days=14)
FOURTEEN_DAYS_TS = int(round(fourteen_days_ago.timestamp() * 1_000_000))
FOURTEEN_DAYS_STR = datetime.datetime.fromtimestamp(FOURTEEN_DAYS_TS / 1_000_000).strftime("%Y-%m-%d")
TODAY_YMD = datetime.date.today().strftime("%Y-%m-%d")


def cleanup() -> None:
    """Removes temp files"""

    if os.path.exists(DB_FILE_PATH):
        os.remove(DB_FILE_PATH)

    # remove api mlrun path
    shutil.rmtree(STORAGE_PATH, ignore_errors=True)

    # remove api local path
    shutil.rmtree("local", ignore_errors=True)

    # remove test experiment mlrun path
    shutil.rmtree("mlruns", ignore_errors=True)

    # remove test folder for loading model
    shutil.rmtree("loader_test", ignore_errors=True)


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
def gcp_cred_path():
    return os.path.join(os.path.dirname(__file__), "assets/fake_gcp_creds.json")


def save_path():
    return f"blob/{uuid.uuid4().hex}"


@pytest.fixture(scope="function")
def mock_gcp_vars(gcp_cred_path):
    creds, _ = load_credentials_from_file(gcp_cred_path)
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
        "opsml.helpers.gcp_utils.GcpCredsSetter",
        get_creds=MagicMock(return_value=creds),
    ) as mock_gcp_creds:
        yield mock_gcp_creds


@pytest.fixture(scope="function")
def gcp_storage_client(mock_gcp_vars):
    gcs_settings = GcsStorageClientSettings(
        storage_type="gcs",
        storage_uri="gs://test",
        credentials=mock_gcp_vars["gcp_creds"],
        gcp_project=mock_gcp_vars["gcp_project"],
    )
    storage_client = StorageClientGetter.get_storage_client(storage_settings=gcs_settings)
    return storage_client


@pytest.fixture(scope="function")
def local_storage_client():
    storage_client = StorageClientGetter.get_storage_client(storage_settings=StorageClientSettings())
    return storage_client


@pytest.fixture(scope="session", autouse=True)
def mock_gcsfs():
    with patch.multiple(
        "gcsfs.GCSFileSystem",
        ls=MagicMock(return_value=["test"]),
        upload=MagicMock(return_value=True),
        download=MagicMock(return_value="gs://test"),
    ) as mocked_gcsfs:
        yield mocked_gcsfs


@pytest.fixture(scope="function")
def mock_pathlib():
    with patch.multiple(
        "pathlib.Path",
        mkdir=MagicMock(return_value=None),
    ) as mocked_pathlib:
        yield mocked_pathlib


@pytest.fixture(scope="function")
def mock_joblib_storage(mock_pathlib):
    with patch.multiple(
        "opsml.registry.storage.artifact_storage.JoblibStorage",
        _write_joblib=MagicMock(return_value=None),
        _load_artifact=MagicMock(return_value=None),
    ) as mocked_joblib:
        yield mocked_joblib


@pytest.fixture(scope="function")
def mock_json_storage(mock_pathlib):
    with patch.multiple(
        "opsml.registry.storage.artifact_storage.JSONStorage",
        _write_json=MagicMock(return_value=None),
        _load_artifact=MagicMock(return_value=None),
    ) as mocked_json:
        yield mocked_json


@pytest.fixture(scope="function")
def mock_artifact_storage_clients(mock_json_storage, mock_joblib_storage):
    yield mock_json_storage, mock_joblib_storage


@pytest.fixture(scope="function")
def mock_pyarrow_parquet_write(mock_pathlib):
    with patch.multiple("pyarrow.parquet", write_table=MagicMock(return_value=True)) as mock_:
        yield mock_


@pytest.fixture(scope="function")
def mock_pyarrow_parquet_dataset(mock_pathlib, test_df, test_arrow_table):
    with patch("pyarrow.parquet.ParquetDataset") as mock_:
        mock_dataset = mock_.return_value
        mock_dataset.read.return_value = test_arrow_table
        mock_dataset.read.to_pandas.return_value = test_df

        yield mock_dataset


################################################################################
# Mocks
################################################################################


@pytest.fixture(scope="module")
def test_app() -> Iterator[TestClient]:
    cleanup()
    from opsml.app.main import OpsmlApp

    opsml_app = OpsmlApp(run_mlflow=True)
    with TestClient(opsml_app.get_app()) as tc:
        yield tc
    cleanup()


@pytest.fixture(scope="module")
def test_app_login() -> Iterator[TestClient]:
    cleanup()
    from opsml.app.main import OpsmlApp

    opsml_app = OpsmlApp(run_mlflow=True, login=True)
    with TestClient(opsml_app.get_app()) as tc:
        yield tc
    cleanup()


def mock_registries(test_client: TestClient) -> CardRegistries:
    def callable_api():
        return test_client

    with patch("httpx.Client", callable_api) as mock_client:
        from opsml.registry.sql.settings import settings

        settings.opsml_tracking_uri = "http://testserver"
        registries = CardRegistries()

        engine = registries.model._registry._engine
        initializer = DBInitializer(engine=engine)
        initializer.initialize()

        registries.data = ClientCardRegistry(registry_name="data")
        registries.model = ClientCardRegistry(registry_name="model")
        registries.pipeline = ClientCardRegistry(registry_name="pipeline")
        registries.run = ClientCardRegistry(registry_name="run")
        registries.project = ClientCardRegistry(registry_name="project")

        return registries


def mlflow_storage_client():
    mlflow_storage = StorageClientGetter.get_storage_client(
        storage_settings=StorageClientSettings(
            storage_type=StorageSystem.MLFLOW.value,
            storage_uri=STORAGE_PATH,
        )
    )
    return mlflow_storage


def mock_mlflow_project(info: ProjectInfo) -> MlflowProject:
    info.tracking_uri = SQL_PATH
    mlflow_exp: MlflowProject = get_project(info)

    api_card_registries = CardRegistries()
    api_card_registries.data = ClientCardRegistry(registry_name="data")
    api_card_registries.model = ClientCardRegistry(registry_name="model")
    api_card_registries.run = ClientCardRegistry(registry_name="run")
    api_card_registries.project = ClientCardRegistry(registry_name="project")
    api_card_registries.pipeline = ClientCardRegistry(registry_name="pipeline")

    # set storage client
    mlflow_storage = mlflow_storage_client()

    api_card_registries.set_storage_client(mlflow_storage)
    mlflow_exp._run_mgr.registries = api_card_registries
    mlflow_exp._run_mgr._storage_client = mlflow_storage
    mlflow_exp._run_mgr._storage_client.mlflow_client = mlflow_exp._run_mgr.mlflow_client

    return mlflow_exp


@pytest.fixture(scope="function")
def api_registries(test_app: TestClient) -> Iterator[dict[str, ClientCardRegistry]]:
    yield mock_registries(test_app)


@pytest.fixture(scope="function")
def mock_cli_property(api_registries):
    with patch("opsml.cli.utils.CliApiClient.client", new_callable=PropertyMock) as client_mock:
        from opsml.registry.sql.settings import settings

        client_mock.return_value = settings.request_client
        yield client_mock


@pytest.fixture(scope="function")
def api_storage_client(api_registries):
    return api_registries.data._registry.storage_client


@pytest.fixture(scope="function")
def mock_app_config_token(api_registries):
    with patch("opsml.app.core.config.OpsmlConfig.PROD_TOKEN", new_callable=PropertyMock) as attr_mock:
        attr_mock.return_value = "fail"

        yield attr_mock


@pytest.fixture(scope="function")
def mlflow_project(api_registries: CardRegistries) -> Iterator[MlflowProject]:
    info = ProjectInfo(name="test_exp", team="test", user_email="test", tracking_uri=SQL_PATH)
    mlflow_exp: MlflowProject = get_project(info=info)

    mlflow_storage = mlflow_storage_client()
    api_registries.set_storage_client(mlflow_storage)
    mlflow_exp._run_mgr.registries = api_registries

    mlflow_exp._run_mgr._storage_client = mlflow_storage
    mlflow_exp._run_mgr._storage_client.mlflow_client = mlflow_exp._run_mgr.mlflow_client

    yield mlflow_exp


@pytest.fixture(scope="function")
def opsml_project(api_registries: CardRegistries) -> Iterator[OpsmlProject]:
    opsml_run = OpsmlProject(
        info=ProjectInfo(
            name="test_exp",
            team="test",
            user_email="test",
            tracking_uri=SQL_PATH,
        )
    )
    opsml_run._run_mgr.registries = api_registries
    return opsml_run


def mock_opsml_project(info: ProjectInfo) -> MlflowProject:
    info.tracking_uri = SQL_PATH
    opsml_run = OpsmlProject(info=info)

    api_card_registries = CardRegistries()
    api_card_registries.data = ClientCardRegistry(registry_name="data")
    api_card_registries.model = ClientCardRegistry(registry_name="model")
    api_card_registries.run = ClientCardRegistry(registry_name="run")
    api_card_registries.project = ClientCardRegistry(registry_name="project")
    api_card_registries.pipeline = ClientCardRegistry(registry_name="pipeline")

    opsml_run._run_mgr.registries = api_card_registries
    return opsml_run


@pytest.fixture(scope="function")
def mock_typer():
    with patch.multiple("typer", launch=MagicMock(return_value=0)) as mock_typer:
        yield mock_typer


@pytest.fixture(scope="function")
def mock_opsml_app_run():
    with patch.multiple("opsml.app.main.OpsmlApp", run=MagicMock(return_value=0)) as mock_opsml_app_run:
        yield mock_opsml_app_run


######## local clients


@pytest.fixture(scope="module")
def experiment_table_to_migrate():
    from sqlalchemy import Column, JSON, String
    from sqlalchemy.orm import declarative_mixin

    @declarative_mixin
    class ExperimentMixin:
        data_card_uids = Column("data_card_uids", JSON)
        model_card_uids = Column("model_card_uids", JSON)
        pipeline_card_uid = Column("pipeline_card_uid", String(512))
        project_id = Column("project_id", String(512))
        artifact_uris = Column("artifact_uris", JSON)
        metrics = Column("metrics", JSON)
        parameters = Column("parameters", JSON)
        tags = Column("tags", JSON)

    class ExperimentSchema(Base, BaseMixin, ExperimentMixin):  # type: ignore
        __tablename__ = "OPSML_EXPERIMENT_REGISTRY"

        def __repr__(self):
            return f"<SqlMetric({self.__tablename__}"

    yield ExperimentSchema


@pytest.fixture(scope="function")
def mock_local_engine():
    local_client = LocalSQLConnection(tracking_uri="sqlite://")
    engine = local_client.get_engine()
    return


@pytest.fixture(scope="module")
def db_registries():
    # force opsml to use CardRegistry with SQL connection (non-proxy)
    from opsml.registry.sql.registry import CardRegistry

    model_registry = CardRegistry(registry_name="model")
    data_registry = CardRegistry(registry_name="data")
    run_registry = CardRegistry(registry_name="run")
    pipeline_registry = CardRegistry(registry_name="pipeline")

    engine = model_registry._registry._engine

    initializer = DBInitializer(engine=engine)
    # tables are created when settings are called.
    # settings is a singleton, so during testing, if the tables are deleted, they are not re-created
    # need to do it manually

    initializer.initialize()

    yield {
        "data": data_registry,
        "model": model_registry,
        "run": run_registry,
        "pipeline": pipeline_registry,
    }

    cleanup()


@pytest.fixture(scope="function")
def mock_model_cli_loader(db_registries):
    model_registry = db_registries["model"]
    from opsml.cli.load_model_card import ModelLoader

    class MockModelLoader(ModelLoader):
        @property
        def base_path(self) -> str:
            return "loader_test"

        def _set_registry(self) -> Any:
            return model_registry

    with patch("opsml.cli.load_model_card.ModelLoader", MockModelLoader) as mock_cli_loader:
        yield mock_cli_loader


@pytest.fixture(scope="function")
def mock_gcs_storage_response():
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                "storage_type": "gcs",
                "storage_uri": "gs://test",
                "proxy": False,
            }

    class MockHTTPX(httpx.Client):
        def get(self, url, **kwargs):
            return MockResponse()

    with patch("httpx.Client", MockHTTPX) as mock_requests:
        yield mock_requests


@pytest.fixture(scope="function")
def mock_gcs(test_df):
    class StorageClient:
        def bucket(self, gcs_bucket: str):
            return Bucket()

        def blob(self, blob_path: str):
            return Blob()

        def list_blobs(self, prefix: str):
            return [Blob(), Blob()]

    class MockStorage(GCSStorageClient):
        def __init__(self):
            self.client = StorageClient()

    with patch("opsml.helpers.gcp_utils.GCSStorageClient", MockStorage) as mock_storage:
        yield mock_storage


######### Data for registry tests
@pytest.fixture(scope="function")
def test_array():
    data = np.random.rand(10, 100)
    return data


@pytest.fixture(scope="function")
def test_split_array():
    indices = np.array([0, 1, 2])
    return [DataSplit(label="train", indices=indices)]


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


@pytest.fixture(scope="session")
def test_polars_dataframe():
    df = pl.DataFrame(
        {
            "foo": [1, 2, 3, 4, 5, 6],
            "bar": ["a", "b", "c", "d", "e", "f"],
            "y": [1, 2, 3, 4, 5, 6],
        }
    )
    return df


@pytest.fixture(scope="function")
def pandas_timestamp_df():
    df = pd.DataFrame({"date": ["2014-10-23", "2016-09-08", "2016-10-08", "2020-10-08"]})
    df["date"] = pd.to_datetime(df["date"])
    return df


@pytest.fixture(scope="session")
def test_polars_split():
    return [DataSplit(label="train", column_name="foo", column_value=0)]


@pytest.fixture(scope="module")
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


###############################################################################
# Models
################################################################################


@pytest.fixture(scope="session")
def regression_data():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3

    return X, y


@pytest.fixture(scope="session")
def regression_data_polars(regression_data):
    X, y = regression_data

    data = pl.DataFrame({"col_0": X[:, 0], "col_1": X[:, 1], "y": y})

    return data


@pytest.fixture(scope="session")
def load_pytorch_language():
    import torch
    from transformers import AutoTokenizer

    # model_name = "sshleifer/tiny-distilbert-base-cased"
    tokenizer = AutoTokenizer.from_pretrained("./tests/tokenizer/")
    data = tokenizer(
        "this is a test",
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    sample_data = {name: values.numpy() for name, values in data.items()}
    loaded_model = torch.load("tests/assets/distill-bert-tiny.pt", torch.device("cpu"))

    return loaded_model, sample_data


@pytest.fixture(scope="session")
def pytorch_onnx_byo():
    from torch import nn
    import torch.utils.model_zoo as model_zoo
    import torch.onnx
    import onnx

    # Super Resolution model definition in PyTorch
    import torch.nn as nn
    import torch.nn.init as init

    class SuperResolutionNet(nn.Module):
        def __init__(self, upscale_factor, inplace=False):
            super(SuperResolutionNet, self).__init__()

            self.relu = nn.ReLU(inplace=inplace)
            self.conv1 = nn.Conv2d(1, 64, (5, 5), (1, 1), (2, 2))
            self.conv2 = nn.Conv2d(64, 64, (3, 3), (1, 1), (1, 1))
            self.conv3 = nn.Conv2d(64, 32, (3, 3), (1, 1), (1, 1))
            self.conv4 = nn.Conv2d(32, upscale_factor**2, (3, 3), (1, 1), (1, 1))
            self.pixel_shuffle = nn.PixelShuffle(upscale_factor)

            self._initialize_weights()

        def forward(self, x):
            x = self.relu(self.conv1(x))
            x = self.relu(self.conv2(x))
            x = self.relu(self.conv3(x))
            x = self.pixel_shuffle(self.conv4(x))
            return x

        def _initialize_weights(self):
            init.orthogonal_(self.conv1.weight, init.calculate_gain("relu"))
            init.orthogonal_(self.conv2.weight, init.calculate_gain("relu"))
            init.orthogonal_(self.conv3.weight, init.calculate_gain("relu"))
            init.orthogonal_(self.conv4.weight)

    # Create the super-resolution model by using the above model definition.
    torch_model = SuperResolutionNet(upscale_factor=3)

    # Load pretrained model weights
    model_url = "https://s3.amazonaws.com/pytorch/test_data/export/superres_epoch100-44c6958e.pth"
    batch_size = 1  # just a random number

    # Initialize model with the pretrained weights
    map_location = lambda storage, loc: storage
    if torch.cuda.is_available():
        map_location = None
    torch_model.load_state_dict(model_zoo.load_url(model_url, map_location=map_location))

    # set the model to inference mode
    torch_model.eval()

    # Input to the model
    x = torch.randn(batch_size, 1, 224, 224, requires_grad=True)
    torch_out = torch_model(x)

    with tempfile.TemporaryDirectory() as tmpdir:
        onnx_path = f"{tmpdir}/super_resolution.onnx"
        # Export the model
        torch.onnx.export(
            torch_model,  # model being run
            x,  # model input (or a tuple for multiple inputs)
            onnx_path,  # where to save the model (can be a file or file-like object)
            export_params=True,  # store the trained parameter weights inside the model file
            opset_version=10,  # the ONNX version to export the model to
            do_constant_folding=True,  # whether to execute constant folding for optimization
            input_names=["input"],  # the model's input names
            output_names=["output"],  # the model's output names
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},  # variable length axes
        )

        onnx_model = onnx.load(onnx_path)

    model_def = OnnxModelDefinition(
        onnx_version="1.14.0",
        model_bytes=onnx_model.SerializeToString(),
    )

    return model_def, torch_model, x.detach().numpy()[0:1]


@pytest.fixture(scope="session")
def load_transformer_example():
    import tensorflow as tf

    loaded_model = tf.keras.models.load_model("tests/assets/transformer_example")
    data = np.load("tests/assets/transformer_data.npy")
    return loaded_model, data


@pytest.fixture(scope="function")
def load_multi_input_keras_example():
    import tensorflow as tf

    loaded_model = tf.keras.models.load_model("tests/assets/multi_input_example")
    data = joblib.load("tests/assets/multi_input_data.joblib")
    return loaded_model, data


@pytest.fixture(scope="session")
def load_pytorch_resnet():
    import torch

    loaded_model = torch.load("tests/assets/resnet.pt")
    data = torch.randn(1, 3, 224, 224).numpy()

    return loaded_model, data


@pytest.fixture(scope="session")
def iris_data() -> pd.DataFrame:
    iris = load_iris()
    feature_names = ["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"]
    x = pd.DataFrame(data=np.c_[iris["data"]], columns=feature_names)
    x["target"] = iris["target"]

    return x


@pytest.fixture(scope="session")
def iris_data_polars() -> pl.DataFrame:
    iris = load_iris()
    feature_names = ["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"]
    x = pd.DataFrame(data=np.c_[iris["data"]], columns=feature_names)
    x["target"] = iris["target"]

    return pl.from_pandas(data=x)


@pytest.fixture(scope="function")
def stacking_regressor(regression_data):
    X, y = regression_data
    estimators = [
        ("lr", ensemble.RandomForestRegressor(n_estimators=5)),
        ("svr", XGBRegressor(n_estimators=3, max_depth=3)),
        ("reg", lgb.LGBMRegressor(n_estimators=3, max_depth=3, num_leaves=5, objective="quantile", alpha="0.5")),
    ]
    reg = ensemble.StackingRegressor(
        estimators=estimators,
        final_estimator=ensemble.RandomForestRegressor(n_estimators=5, random_state=42),
        cv=2,
    )
    reg.fit(X, y)
    return reg, X


@pytest.fixture(scope="session")
def sklearn_pipeline() -> tuple[Pipeline, pd.DataFrame]:
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
    pipe = Pipeline(
        [("preprocess", preprocessor), ("rf", lgb.LGBMRegressor(n_estimators=3, max_depth=3, num_leaves=5))]
    )
    pipe.fit(train_data, data["y"])
    return pipe, train_data


@pytest.fixture(scope="session")
def sklearn_pipeline_advanced() -> tuple[Pipeline, pd.DataFrame]:
    X, y = fetch_openml("titanic", version=1, as_frame=True, return_X_y=True, parser="pandas")

    numeric_features = ["age", "fare"]
    numeric_transformer = Pipeline(steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])

    categorical_features = ["embarked", "sex", "pclass"]
    categorical_transformer = Pipeline(
        steps=[
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ("selector", SelectPercentile(chi2, percentile=50)),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    clf = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", linear_model.LogisticRegression(max_iter=5))])

    X_train, X_test, y_train, y_test = train_test_split(X[:1000], y[:1000], test_size=0.2, random_state=0)

    features = [*numeric_features, *categorical_features]
    X_train = X_train[features]
    y_train = y_train.to_numpy().astype(np.int32)

    clf.fit(X_train, y_train)
    return clf, X_train[:100]


@pytest.fixture(scope="function")
def xgb_df_regressor(drift_dataframe):
    X_train, y_train, X_test, y_test = drift_dataframe
    reg = XGBRegressor(n_estimators=5, max_depth=3)
    reg.fit(X_train.to_numpy(), y_train)
    return reg, X_train[:100]


@pytest.fixture(scope="function")
def random_forest_classifier(drift_dataframe):
    X_train, y_train, X_test, y_test = drift_dataframe
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X_train.to_numpy(), y_train)
    return reg, X_train[:100]


@pytest.fixture(scope="function")
def lgb_classifier(drift_dataframe):
    X_train, y_train, X_test, y_test = drift_dataframe
    reg = lgb.LGBMClassifier(
        n_estimators=3,
        max_depth=3,
        num_leaves=5,
    )
    reg.fit(X_train.to_numpy(), y_train)
    return reg, X_train[:100]


@pytest.fixture(scope="function")
def lgb_booster_dataframe(drift_dataframe):
    X_train, y_train, X_test, y_test = drift_dataframe
    # create dataset for lightgbm
    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)
    # specify your configurations as a dict
    params = {
        "boosting_type": "gbdt",
        "objective": "regression",
        "metric": {"l2", "l1"},
        "num_leaves": 31,
        "learning_rate": 0.05,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": 0,
    }
    # train
    gbm = lgb.train(
        params, lgb_train, num_boost_round=20, valid_sets=lgb_eval, callbacks=[lgb.early_stopping(stopping_rounds=5)]
    )

    return gbm, X_train[:100]


@pytest.fixture(scope="module")
def linear_regression_polars(regression_data_polars: pl.DataFrame):
    data: pl.DataFrame = regression_data_polars

    X = data.select(pl.col(["col_0", "col_1"]))
    y = data.select(pl.col("y"))

    reg = linear_model.LinearRegression().fit(
        X.to_numpy(),
        y.to_numpy(),
    )
    return reg, X


@pytest.fixture(scope="module")
def linear_regression(regression_data):
    X, y = regression_data
    reg = linear_model.LinearRegression().fit(X, y)
    return reg, X


@pytest.fixture(scope="function")
def test_model_card(sklearn_pipeline):
    model, data = sklearn_pipeline
    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        version="1.0.0",
        uris=ModelCardUris(trained_model_uri="test"),
    )
    return model_card


################################################################

### API mocks

#################################################################


@pytest.fixture(scope="function")
def linear_reg_api_example():
    return 6.0, {"inputs": [1, 1]}


@pytest.fixture(scope="function")
def random_forest_api_example():
    record = {
        "col_0": -0.8720515927961947,
        "col_1": -3.2912296580011247,
        "col_2": -4.933565864371848,
        "col_3": -4.760871124559602,
        "col_4": -4.663587917354173,
        "col_5": -9.116647051793624,
        "col_6": -4.154678055358668,
        "col_7": -4.670396869411925,
        "col_8": -4.392686260289228,
        "col_9": -5.314893665635682,
        "col_10": 2.0,
    }

    return 2, record


@pytest.fixture(scope="function")
def tensorflow_api_example():
    record = {
        "title": [6448.0, 1046.0, 5305.0, 61.0, 6536.0, 6846.0, 7111.0, 2616.0, 8486.0, 6376.0],
        "body": [
            8773.0,
            834.0,
            8479.0,
            2176.0,
            4610.0,
            8978.0,
            1843.0,
            9090.0,
            108.0,
            1894.0,
            5109.0,
            5259.0,
            6029.0,
            3274.0,
            4893.0,
            6842.0,
            5180.0,
            3806.0,
            7638.0,
            7974.0,
            6575.0,
            7027.0,
            8622.0,
            4418.0,
            7190.0,
            7566.0,
            8229.0,
            8612.0,
            9264.0,
            2129.0,
            8997.0,
            3908.0,
            6012.0,
            3212.0,
            649.0,
            3030.0,
            3538.0,
            723.0,
            7829.0,
            7891.0,
            578.0,
            2080.0,
            6893.0,
            8127.0,
            7131.0,
            1405.0,
            9556.0,
            8495.0,
            3976.0,
            5414.0,
            1994.0,
            5236.0,
            3162.0,
            7749.0,
            3275.0,
            2963.0,
            2403.0,
            6157.0,
            5980.0,
            1788.0,
            6849.0,
            5209.0,
            4861.0,
            281.0,
            7498.0,
            5745.0,
            891.0,
            1681.0,
            5208.0,
            21.0,
            7302.0,
            2131.0,
            5611.0,
            476.0,
            8018.0,
            1996.0,
            3719.0,
            5497.0,
            5153.0,
            5819.0,
            3545.0,
            3935.0,
            5961.0,
            5283.0,
            8219.0,
            7065.0,
            9959.0,
            5395.0,
            3522.0,
            7269.0,
            3448.0,
            4219.0,
            8831.0,
            7094.0,
            5242.0,
            2099.0,
            6223.0,
            3535.0,
            551.0,
            4417.0,
        ],
        "tags": [1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    }
    prediction = {
        "priority": 0.22161353,
        "department": [-0.4160802, -0.27275354, 0.67165923, 0.37333506],
    }
    return prediction, record


@pytest.fixture(scope="function")
def sklearn_pipeline_api_example():
    record = {"CAT1": "a", "CAT2": "c", "num1": 0.5, "num2": 0.6, "num3": 0}

    return 0.5, record


@pytest.fixture(scope="module")
def test_fastapi_client(fastapi_model_app):
    with TestClient(fastapi_model_app) as test_client:
        yield test_client


##### Sklearn estimators for onnx
@pytest.fixture(scope="module")
def ard_regression(regression_data):
    X, y = regression_data
    reg = linear_model.ARDRegression().fit(X, y)
    return reg, X


@pytest.fixture(scope="session")
def classification_data():
    from sklearn.datasets import make_classification

    X, y = make_classification(
        n_samples=1000,
        n_features=4,
        n_informative=2,
        n_redundant=0,
        random_state=0,
        shuffle=False,
    )
    return X, y


@pytest.fixture(scope="module")
def ada_boost_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.AdaBoostClassifier(n_estimators=5, random_state=0)
    clf.fit(X, y)
    return clf, X


@pytest.fixture(scope="module")
def ada_regression(regression_data):
    X, y = regression_data
    reg = ensemble.AdaBoostRegressor(n_estimators=5).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def bagging_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.BaggingClassifier(n_estimators=5)
    clf.fit(X, y)
    return clf, X


@pytest.fixture(scope="module")
def bagging_regression(regression_data):
    X, y = regression_data
    reg = ensemble.BaggingRegressor(n_estimators=5).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def bayesian_ridge_regression(regression_data):
    X, y = regression_data
    reg = linear_model.BayesianRidge(n_iter=10).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def bernoulli_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.BernoulliNB(force_alpha=True).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def categorical_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.CategoricalNB(force_alpha=True).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def complement_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.ComplementNB(force_alpha=True).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def decision_tree_regressor(regression_data):
    X, y = regression_data
    reg = tree.DecisionTreeRegressor(max_depth=5).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def decision_tree_classifier():
    data = pd.read_csv("tests/assets/titanic.csv", index_col=False)
    data["AGE"] = data["AGE"].astype("float64")

    X = data
    y = data.pop("SURVIVED")

    clf = tree.DecisionTreeClassifier(max_depth=5).fit(X, y)
    clf.fit(X, y)
    return clf, X


@pytest.fixture(scope="module")
def elastic_net(regression_data):
    X, y = regression_data
    reg = linear_model.ElasticNet(max_iter=10).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def elastic_net_cv(regression_data):
    X, y = regression_data
    reg = linear_model.ElasticNetCV(max_iter=10, cv=2).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def extra_tree_regressor(regression_data):
    X, y = regression_data
    reg = tree.ExtraTreeRegressor(max_depth=5).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def extra_trees_regressor(regression_data):
    X, y = regression_data
    reg = ensemble.ExtraTreesRegressor(n_estimators=5).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def extra_tree_classifier(classification_data):
    X, y = classification_data
    clf = tree.ExtraTreeClassifier(max_depth=5).fit(X, y)
    clf.fit(X, y)
    return clf, X


@pytest.fixture(scope="module")
def extra_trees_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.ExtraTreesClassifier(n_estimators=5).fit(X, y)
    clf.fit(X, y)
    return clf, X


@pytest.fixture(scope="module")
def gamma_regressor(regression_data):
    X, y = regression_data
    reg = linear_model.GammaRegressor(max_iter=5).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def gaussian_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.GaussianNB().fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def gaussian_process_regressor(regression_data):
    X, y = regression_data
    reg = gaussian_process.GaussianProcessRegressor().fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def gradient_booster_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.GradientBoostingClassifier(n_estimators=5)
    clf.fit(X, y)
    return clf, X


@pytest.fixture(scope="module")
def gradient_booster_regressor(regression_data):
    X, y = regression_data
    reg = clf = ensemble.GradientBoostingRegressor(n_estimators=5).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def hist_booster_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.HistGradientBoostingClassifier(max_iter=5)
    clf.fit(X, y)
    return clf, X


@pytest.fixture(scope="module")
def hist_booster_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = ensemble.HistGradientBoostingRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def huber_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.HuberRegressor(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def knn_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = neighbors.KNeighborsRegressor(n_neighbors=2).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def knn_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    clf = neighbors.KNeighborsClassifier(n_neighbors=2).fit(X_train, y_train)
    return clf, X_train


@pytest.fixture(scope="module")
def lars_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.Lars().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lars_cv_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.LarsCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.Lasso().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_cv_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.LassoCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_lars_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.LassoLars().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_lars_cv_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.LassoLarsCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_lars_ic_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.LassoLarsIC().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def linear_svc(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = svm.LinearSVC(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def linear_svr(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = svm.LinearSVR(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def logistic_regression_cv(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.LogisticRegressionCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def mlp_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = neural_network.MLPClassifier(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def mlp_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = neural_network.MLPRegressor(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def multioutput_classification():
    from sklearn.datasets import make_multilabel_classification

    X, y = make_multilabel_classification(n_classes=3, random_state=0)
    reg = multioutput.MultiOutputClassifier(linear_model.LogisticRegression()).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def multioutput_regression():
    from sklearn.datasets import load_linnerud

    X, y = load_linnerud(return_X_y=True)
    reg = multioutput.MultiOutputRegressor(linear_model.Ridge(random_state=123)).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def multitask_elasticnet():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskElasticNet(alpha=0.1).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def multitask_elasticnet_cv():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskElasticNetCV(max_iter=5, cv=2).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def multitask_lasso():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskLasso(alpha=0.1).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def multitask_lasso_cv():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskLassoCV(max_iter=5, cv=2).fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def multinomial_nb():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([1, 2, 3])
    reg = naive_bayes.MultinomialNB().fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def nu_svc(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = svm.NuSVC(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def nu_svr(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = svm.NuSVR(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def pls_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = cross_decomposition.PLSRegression(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def passive_aggressive_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.PassiveAggressiveClassifier(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def passive_aggressive_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.PassiveAggressiveRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def perceptron(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.Perceptron(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def poisson_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.PoissonRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def quantile_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.QuantileRegressor(solver="highs").fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ransac_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.RANSACRegressor(max_trials=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def radius_neighbors_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = neighbors.RadiusNeighborsRegressor().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def radius_neighbors_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    clf = neighbors.RadiusNeighborsClassifier().fit(X_train, y_train)
    return clf, X_train


@pytest.fixture(scope="module")
def ridge_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.Ridge().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ridge_cv_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.RidgeCV(cv=2).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ridge_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = linear_model.RidgeClassifier(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ridge_cv_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = reg = linear_model.RidgeClassifierCV(cv=2).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def sgd_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = reg = linear_model.SGDClassifier(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def sgd_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = reg = linear_model.SGDRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def svc(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = svm.SVC(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def svr(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = svm.SVR(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def stacking_classifier():
    from sklearn.datasets import load_iris
    from sklearn.pipeline import make_pipeline

    X, y = load_iris(return_X_y=True)
    estimators = [
        ("rf", ensemble.RandomForestClassifier(n_estimators=10, random_state=42)),
        ("svr", make_pipeline(StandardScaler(), linear_model.LogisticRegression(max_iter=5))),
    ]
    reg = ensemble.StackingClassifier(
        estimators=estimators, final_estimator=linear_model.LogisticRegression(max_iter=5)
    )
    reg.fit(X, y)
    return reg, X


@pytest.fixture(scope="module")
def theilsen_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = reg = linear_model.TheilSenRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def tweedie_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    reg = reg = linear_model.TweedieRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def voting_classifier(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    clf1 = linear_model.LogisticRegression(multi_class="multinomial", max_iter=5)
    clf2 = ensemble.RandomForestClassifier(n_estimators=5, random_state=1)
    clf3 = naive_bayes.GaussianNB()
    eclf1 = ensemble.VotingClassifier(
        estimators=[("lr", clf1), ("rf", clf2), ("gnb", clf3)], voting="hard", flatten_transform=False
    )
    eclf1 = eclf1.fit(X_train, y_train)
    return eclf1, X_train


@pytest.fixture(scope="module")
def voting_regressor(drift_dataframe):
    X_train, y_train, _, _ = drift_dataframe
    clf1 = linear_model.LinearRegression()
    clf2 = ensemble.RandomForestRegressor(n_estimators=5, random_state=1)
    clf3 = linear_model.Lasso()
    eclf1 = ensemble.VotingRegressor(estimators=[("lr", clf1), ("rf", clf2), ("lso", clf3)])
    eclf1 = eclf1.fit(X_train, y_train)
    return eclf1, X_train
