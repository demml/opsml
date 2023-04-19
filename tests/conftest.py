from typing import Any, Iterator

import os
import pathlib

# setting initial env vars to override default sql db
# these must be set prior to importing opsml sicne they establish their
DB_FILE_PATH = str(pathlib.Path.home().joinpath("tmp.db"))
SQL_PATH = f"sqlite:///{DB_FILE_PATH}"
STORAGE_PATH = str(pathlib.Path.home().joinpath("mlruns"))

os.environ["OPSML_TRACKING_URI"] = SQL_PATH
os.environ["OPSML_STORAGE_URI"] = STORAGE_PATH
os.environ["_MLFLOW_SERVER_ARTIFACT_DESTINATION"] = STORAGE_PATH
os.environ["_MLFLOW_SERVER_ARTIFACT_ROOT"] = "mlflow-artifacts:/"
os.environ["_MLFLOW_SERVER_FILE_STORE"] = SQL_PATH
os.environ["_MLFLOW_SERVER_SERVE_ARTIFACTS"] = "true"

import uuid
import pytest
import shutil
import httpx
from google.auth import load_credentials_from_file
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

import pyarrow as pa
from pydantic import BaseModel

import numpy as np
import joblib
import pandas as pd

# ml model packages and classes
from sklearn.datasets import fetch_openml
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.ensemble import StackingRegressor
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import lightgbm as lgb


# opsml
from opsml.registry import ModelCard
from opsml.helpers.gcp_utils import GcpCreds, GCPMLScheduler, GCSStorageClient
from opsml.registry.storage.types import StorageClientSettings, GcsStorageClientSettings
from opsml.registry.sql.sql_schema import BaseMixin, Base, DBInitializer
from opsml.registry.sql.connectors.connector import LocalSQLConnection
from opsml.registry.storage.storage_system import StorageClientGetter, StorageSystem
from opsml.projects import get_project
from opsml.projects.mlflow import MlflowProject
from opsml.projects.base.types import ProjectInfo
from opsml.registry import CardRegistries
from opsml.projects import OpsmlProject


# testing
from tests.mock_api_registries import CardRegistry as ClientCardRegistry

CWD = os.getcwd()


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


def mock_registries(test_client: TestClient) -> dict[str, ClientCardRegistry]:
    def callable_api():
        return test_client

    with patch("httpx.Client", callable_api):

        from opsml.helpers.settings import settings

        settings.opsml_tracking_uri = "http://testserver"
        registries = CardRegistries()

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
def api_storage_client(api_registries):
    return api_registries.data.registry.storage_client


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
        params = Column("params", JSON)
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

    engine = model_registry.registry._engine

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
    from pathlib import Path
    from opsml.scripts.load_model_card import ModelLoader
    from opsml.registry.model.types import ModelApiDef

    class MockModelLoader(ModelLoader):
        def _write_api_json(self, api_def: ModelApiDef, filepath: Path) -> None:
            pass

        def _set_registry(self) -> Any:
            return model_registry

    with patch("opsml.scripts.load_model_card.ModelLoader", MockModelLoader) as mock_cli_loader:

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
def mock_gcp_scheduler():
    class ScheduleClient:
        def common_location_path(self, project: str, location: str):
            return f"{project}-{location}"

        def list_jobs(self, parent: str):
            return [Blob(name="test")]

        def delete_job(self, job_name: str):
            return True

        def create_job(self, parent: str, job: str):
            return "test_job"

    class MockScheduler(GCPMLScheduler):
        def __init__(self):
            self.schedule_client = ScheduleClient()
            self.oidc_token = "test"
            self.parent_path = "test"

        def _create_job_class(self, job: dict):
            return "job"

    with patch("opsml.helpers.gcp_utils.GCPMLScheduler", MockScheduler) as mock_scheduler:

        yield mock_scheduler


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


###############################################################################
# Moodels
################################################################################


@pytest.fixture(scope="session")
def load_pytorch_language():

    import torch
    from transformers import AutoTokenizer

    model_name = "sshleifer/tiny-distilbert-base-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
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


@pytest.fixture(scope="function")
def stacking_regressor():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    estimators = [("lr", RandomForestRegressor()), ("svr", XGBRegressor()), ("reg", lgb.LGBMRegressor())]
    reg = StackingRegressor(
        estimators=estimators,
        final_estimator=RandomForestRegressor(n_estimators=10, random_state=42),
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
    pipe = Pipeline([("preprocess", preprocessor), ("rf", lgb.LGBMRegressor())])
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

    clf = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", LogisticRegression())])

    X_train, X_test, y_train, y_test = train_test_split(X[:1000], y[:1000], test_size=0.2, random_state=0)

    features = [*numeric_features, *categorical_features]
    X_train = X_train[features]
    y_train = y_train.to_numpy().astype(np.int32)

    clf.fit(X_train, y_train)
    return clf, X_train[:100]


@pytest.fixture(scope="function")
def xgb_df_regressor(drift_dataframe):
    X_train, y_train, X_test, y_test = drift_dataframe
    reg = XGBRegressor()
    reg.fit(X_train.to_numpy(), y_train)
    return reg, X_train[:100]


@pytest.fixture(scope="function")
def random_forest_classifier(drift_dataframe):
    X_train, y_train, X_test, y_test = drift_dataframe
    reg = RandomForestClassifier(n_estimators=10)
    reg.fit(X_train.to_numpy(), y_train)
    return reg, X_train[:100]


@pytest.fixture(scope="function")
def lgb_classifier(drift_dataframe):
    X_train, y_train, X_test, y_test = drift_dataframe
    reg = lgb.LGBMClassifier(n_estimators=3)
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
def linear_regression():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    reg = LinearRegression().fit(X, y)
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
    )
    return model_card
