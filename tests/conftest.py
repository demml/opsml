import os
import warnings
from pathlib import Path
from typing import Any, Iterator, Optional, Tuple

warnings.filterwarnings("ignore")


# setting initial env vars to override default sql db
# these must be set prior to importing opsml since they establish their
DB_FILE_PATH = "tmp.db"
SQL_PATH = os.environ.get("OPSML_TRACKING_URI", f"sqlite:///{DB_FILE_PATH}")
OPSML_STORAGE_URI = f"{os.getcwd()}/mlruns"
# OPSML_STORAGE_URI = os.environ.get("OPSML_STORAGE_URI", f"{os.getcwd()}/mlruns")

os.environ["APP_ENV"] = "development"
os.environ["OPSML_PROD_TOKEN"] = "test-token"
os.environ["OPSML_TRACKING_URI"] = SQL_PATH
os.environ["OPSML_STORAGE_URI"] = OPSML_STORAGE_URI
os.environ["OPSML_USERNAME"] = "test-user"
os.environ["OPSML_PASSWORD"] = "test-pass"

import datetime
import shutil
import tempfile
import time
import uuid
from unittest.mock import MagicMock, patch

import httpx
import joblib
import lightgbm as lgb
import lightning as L
import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
import pytest
import torch
import torch.nn as nn
from google.auth import load_credentials_from_file
from pydantic import BaseModel
from sklearn import (
    cross_decomposition,
    ensemble,
    gaussian_process,
    linear_model,
    multioutput,
    naive_bayes,
    neighbors,
    neural_network,
    svm,
    tree,
)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer

# ml model packages and classes
from sklearn.datasets import fetch_openml, load_iris
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from starlette.testclient import TestClient
from torch.nn import MSELoss
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset
from xgboost import XGBRegressor

from opsml.helpers.data import create_fake_data
from opsml.helpers.gcp_utils import GcpCreds
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry import CardRegistries, DataSplit, ModelCard

# opsml
from opsml.registry.data.interfaces import (
    ArrowData,
    NumpyData,
    PandasData,
    PolarsData,
    SqlData,
)
from opsml.registry.model.challenger import ModelChallenger
from opsml.registry.model.interfaces import (
    HuggingFaceModel,
    LightGBMModel,
    LightningModel,
    PyTorchModel,
    SklearnModel,
    TensorFlowModel,
)
from opsml.registry.sql.connectors.connector import LocalSQLConnection
from opsml.registry.storage import client
from opsml.registry.types import (
    HuggingFaceOnnxArgs,
    HuggingFaceORTModel,
    HuggingFaceTask,
    Metric,
    OnnxModel,
)
from opsml.settings.config import OpsmlConfig, config

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
    shutil.rmtree(OPSML_STORAGE_URI, ignore_errors=True)

    # remove api local path
    shutil.rmtree("local", ignore_errors=True)

    # remove test experiment mlrun path
    shutil.rmtree("mlruns", ignore_errors=True)

    # remove test folder for loading model
    shutil.rmtree("loader_test", ignore_errors=True)

    # delete test image dir
    shutil.rmtree("test_image_dir", ignore_errors=True)

    # delete blah directory
    shutil.rmtree("blah", ignore_errors=True)

    # delete pytorch lightning logs
    shutil.rmtree("lightning_logs", ignore_errors=True)


# TODO(@damon): Thesee can probably go.
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


@pytest.fixture
def gcp_cred_path():
    return os.path.join(os.path.dirname(__file__), "assets/fake_gcp_creds.json")


def save_path() -> str:
    p = Path(f"mlruns/OPSML_MODEL_REGISTRY/{uuid.uuid4().hex}")
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


@pytest.fixture
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


@pytest.fixture(scope="module")
def tracking_uri():
    return SQL_PATH


@pytest.fixture
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


@pytest.fixture
def gcp_storage_client(mock_gcp_creds, mock_gcsfs):
    return client.get_storage_client(OpsmlConfig(opsml_storage_uri="gs://test"))


@pytest.fixture
def s3_storage_client(mock_s3fs):
    return client.get_storage_client(OpsmlConfig(opsml_storage_uri="s3://test"))


@pytest.fixture
def local_storage_client():
    return client.get_storage_client(OpsmlConfig())


@pytest.fixture
def mock_gcsfs():
    with patch.multiple(
        "gcsfs.GCSFileSystem",
        get=MagicMock(return_value="test"),
        get_mapper=MagicMock(return_value="test"),
        ls=MagicMock(return_value=["test"]),
        put=MagicMock(return_value="test"),
        copy=MagicMock(return_value=None),
        rm=MagicMock(return_value=None),
        exists=MagicMock(return_value=True),
    ) as mocked_gcsfs:
        yield mocked_gcsfs


@pytest.fixture
def mock_s3fs():
    with patch.multiple(
        "s3fs.S3FileSystem",
        get=MagicMock(return_value="test"),
        get_mapper=MagicMock(return_value="test"),
        ls=MagicMock(return_value=["test"]),
        put=MagicMock(return_value="test"),
        copy=MagicMock(return_value=None),
        rm=MagicMock(return_value=None),
        exists=MagicMock(return_value=True),
    ) as mocked_s3fs:
        yield mocked_s3fs


@pytest.fixture
def mock_pathlib():
    with patch.multiple(
        "pathlib.Path",
        mkdir=MagicMock(return_value=None),
    ) as mocked_pathlib:
        yield mocked_pathlib


@pytest.fixture
def mock_joblib_storage(mock_pathlib):
    with patch.multiple(
        "opsml.registry.storage.artifact.JoblibStorage",
        _write_joblib=MagicMock(return_value=None),
        _load_artifact=MagicMock(return_value=None),
    ) as mocked_joblib:
        yield mocked_joblib


@pytest.fixture
def mock_json_storage(mock_pathlib):
    with patch.multiple(
        "opsml.registry.storage.artifact.JSONStorage",
        _write_json=MagicMock(return_value=None),
        _load_artifact=MagicMock(return_value=None),
    ) as mocked_json:
        yield mocked_json


@pytest.fixture
def mock_artifact_storage_clients(mock_json_storage, mock_joblib_storage):
    yield mock_json_storage, mock_joblib_storage


@pytest.fixture
def mock_pyarrow_parquet_write(mock_pathlib):
    with patch.multiple("pyarrow.parquet", write_table=MagicMock(return_value=True)) as mock_:
        yield mock_


@pytest.fixture
def mock_pyarrow_parquet_dataset(mock_pathlib, test_df, test_arrow_table):
    with patch("pyarrow.parquet.ParquetDataset") as mock_:
        mock_dataset = mock_.return_value
        mock_dataset.read.return_value = test_arrow_table
        mock_dataset.read.to_pandas.return_value = test_df

        yield mock_dataset


@pytest.fixture(scope="module")
def test_app() -> Iterator[TestClient]:
    cleanup()
    from opsml.app.main import OpsmlApp

    opsml_app = OpsmlApp()
    with TestClient(opsml_app.get_app()) as tc:
        yield tc
    cleanup()


@pytest.fixture(scope="module")
def test_app_login() -> Iterator[TestClient]:
    cleanup()
    from opsml.app.main import OpsmlApp

    opsml_app = OpsmlApp(login=True)
    with TestClient(opsml_app.get_app()) as tc:
        yield tc
    cleanup()


def mock_registries(monkeypatch: pytest.MonkeyPatch, test_client: TestClient) -> CardRegistries:
    def callable_api():
        return test_client

    with patch("httpx.Client", callable_api):
        # Set the global configuration to mock API "client" mode
        monkeypatch.setattr(config, "opsml_tracking_uri", "http://testserver")

        cfg = OpsmlConfig(opsml_tracking_uri="http://testserver", opsml_storage_uri=OPSML_STORAGE_URI)

        # Cards rely on global storage state - so set it to API
        client.storage_client = client.get_storage_client(cfg)
        return CardRegistries()


@pytest.fixture
def api_registries(monkeypatch: pytest.MonkeyPatch, test_app: TestClient) -> Iterator[CardRegistries]:
    """Returns CardRegistries configured with an API client (to simulate "client" mode)."""
    previous_client = client.storage_client
    yield mock_registries(monkeypatch, test_app)
    client.storage_client = previous_client


@pytest.fixture
def db_registries() -> CardRegistries:
    """Returns CardRegistries configured with a local client (to simulate "client" mode)."""
    cleanup()

    # Cards rely on global storage state - so set it to local.
    client.storage_client = client.get_storage_client(config)
    yield CardRegistries()
    cleanup()


@pytest.fixture
def opsml_project() -> Iterator[OpsmlProject]:
    project = OpsmlProject(
        info=ProjectInfo(
            name="test_exp",
            team="test",
            user_email="test",
        )
    )
    return project


@pytest.fixture
def mock_model_challenger() -> Any:
    class MockModelChallenger(ModelChallenger):
        def __init__(
            self,
            challenger: ModelCard,
            registries: CardRegistries,
        ):
            """
            Instantiates ModelChallenger class

            Args:
                challenger:
                    ModelCard of challenger

            """
            self._challenger = challenger
            self._challenger_metric: Optional[Metric] = None
            self._registries = registries

    return MockModelChallenger


@pytest.fixture
def api_storage_client(api_registries: CardRegistries) -> client.StorageClient:
    return api_registries.data._registry.storage_client


@pytest.fixture
def mock_typer():
    with patch.multiple("typer", launch=MagicMock(return_value=0)) as mock_typer:
        yield mock_typer


@pytest.fixture
def mock_opsml_app_run():
    with patch.multiple("opsml.app.main.OpsmlApp", run=MagicMock(return_value=0)) as mock_opsml_app_run:
        yield mock_opsml_app_run


######## local clients


@pytest.fixture(scope="module")
def experiment_table_to_migrate():
    from sqlalchemy import JSON, Column, String
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


@pytest.fixture
def mock_local_engine():
    local_client = LocalSQLConnection(tracking_uri="sqlite://")
    local_client.get_engine()
    return


@pytest.fixture
def mock_aws_storage_response():
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                "storage_type": "s3",
                "storage_uri": "s3://test",
                "proxy": False,
            }

    class MockHTTPX(httpx.Client):
        def get(self, url, **kwargs):
            return MockResponse()

    with patch("httpx.Client", MockHTTPX) as mock_requests:
        yield mock_requests


@pytest.fixture
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


@pytest.fixture
def real_gcs() -> Iterator[client.StorageClient]:
    prev_client = client.storage_client
    client.storage_client = client.get_storage_client(OpsmlConfig(opsml_storage_uri="gs://shipt-dev"))
    yield client.storage_client
    client.storage_client = prev_client


######### Data for registry tests


@pytest.fixture
def numpy_data() -> np.ndarray[Any, np.float64]:
    data = np.random.rand(10, 100)
    return NumpyData(
        data=data,
        datasplits=[
            DataSplit(label="train", indices=np.array([0, 1, 2])),
        ],
    )


@pytest.fixture
def pandas_data() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "year": [2020, 2022, 2019, 2020, 2020, 2022, 2019, 20211],
            "n_legs": [2, 4, 5, 100, 2, 4, 5, 100],
            "animals": [
                "Flamingo",
                "Horse",
                "Brittle stars",
                "Centipede",
                "Flamingo",
                "Horse",
                "Brittle stars",
                "Centipede",
            ],
        }
    )

    data_split = [
        DataSplit(label="train", column_name="year", column_value=2020),
        DataSplit(label="test", column_name="year", column_value=2021),
    ]
    return PandasData(
        data=df,
        data_splits=data_split,
        sql_logic={"test": "SELECT * FROM TEST_TABLE"},
        dependent_vars=[200, "test"],
    )


@pytest.fixture(scope="session")
def sql_data():
    return SqlData(
        sql_logic={"test": "select * from test_table"},
        feature_descriptions={"test": "test_description"},
    )


@pytest.fixture()
def sql_file():
    return SqlData(
        sql_logic={"test": "test_sql.sql"},
    )


@pytest.fixture(scope="session")
def arrow_data():
    n_legs = pa.array([2, 4, 5, 100])
    animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
    names = ["n_legs", "animals"]
    table = pa.Table.from_arrays([n_legs, animals], names=names)
    return ArrowData(data=table)


@pytest.fixture(scope="session")
def polars_data():
    df = pl.DataFrame(
        {
            "foo": [1, 2, 3, 4, 5, 6],
            "bar": ["a", "b", "c", "d", "e", "f"],
            "y": [1, 2, 3, 4, 5, 6],
        }
    )
    return PolarsData(
        data=df,
        data_splits=[
            DataSplit(
                label="train",
                column_name="foo",
                column_value=0,
            )
        ],
    )


@pytest.fixture
def pandas_timestamp_df():
    df = pd.DataFrame({"date": ["2014-10-23", "2016-09-08", "2016-10-08", "2020-10-08"]})
    df["date"] = pd.to_datetime(df["date"])
    return PandasData(data=df)


@pytest.fixture(scope="session")
def example_dataframe():
    X, y = create_fake_data(n_samples=1000)

    return X, y, X, y


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
def huggingface_language_model():
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

    loaded_model = torch.load("tests/assets/distill-bert-tiny.pt", torch.device("cpu"))

    return PyTorchModel(
        model=loaded_model,
        preprocessor=tokenizer,
        sample_data=dict(data),
    )


@pytest.fixture(scope="module")
def pytorch_simple():
    class Polynomial3(torch.nn.Module):
        def __init__(self):
            """
            In the constructor we instantiate four parameters and assign them as
            member parameters.
            """
            super().__init__()
            self.x1 = torch.nn.Parameter(torch.randn(()))
            self.x2 = torch.nn.Parameter(torch.randn(()))

        def forward(self, x1: torch.Tensor, x2: torch.Tensor):
            """
            In the forward function we accept a Tensor of input data and we must return
            a Tensor of output data. We can use Modules defined in the constructor as
            well as arbitrary operators on Tensors.
            """
            return self.x1 + self.x2 * x1 * x2

    model = Polynomial3()
    inputs = {"x1": torch.randn((1, 1)), "x2": torch.randn((1, 1))}

    return PyTorchModel(
        model=model,
        sample_data=inputs,
        save_args={"as_state_dict": True},
    )


@pytest.fixture(scope="session")
def pytorch_onnx_byo():
    import onnx

    # Super Resolution model definition in PyTorch
    import torch.nn as nn
    import torch.nn.init as init
    import torch.onnx
    import torch.utils.model_zoo as model_zoo
    from torch import nn

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
    def map_location(storage, loc):
        return storage

    if torch.cuda.is_available():
        map_location = None
    torch_model.load_state_dict(model_zoo.load_url(model_url, map_location=map_location))

    # set the model to inference mode
    torch_model.eval()

    # Input to the model
    x = torch.randn(batch_size, 1, 224, 224, requires_grad=True)
    torch_model(x)

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

    model_def = OnnxModel(
        onnx_version="1.14.0",
        model_bytes=onnx_model.SerializeToString(),
    )

    return model_def, torch_model, x.detach().numpy()[0:1]


@pytest.fixture(scope="session")
def tf_transformer_example():
    import tensorflow as tf

    loaded_model = tf.keras.models.load_model("tests/assets/transformer_example")
    data = np.load("tests/assets/transformer_data.npy")

    return TensorFlowModel(model=loaded_model, sample_data=data)


@pytest.fixture
def multi_input_tf_example():
    import tensorflow as tf

    loaded_model = tf.keras.models.load_model("tests/assets/multi_input_example")
    data = joblib.load("tests/assets/multi_input_data.joblib")
    return TensorFlowModel(model=loaded_model, sample_data=data)


@pytest.fixture(scope="session")
def load_pytorch_resnet():
    import torch

    loaded_model = torch.load("tests/assets/resnet.pt")
    data = torch.randn(1, 3, 224, 224).numpy()

    return loaded_model, data


@pytest.fixture(scope="session")
def iris_data() -> PandasData:
    iris = load_iris()
    feature_names = ["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"]
    x = pd.DataFrame(data=np.c_[iris["data"]], columns=feature_names)
    x["target"] = iris["target"]

    return PandasData(data=x, dependent_vars=["target"])


@pytest.fixture(scope="session")
def iris_data_polars() -> PolarsData:
    iris = load_iris()
    feature_names = ["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"]
    x = pd.DataFrame(data=np.c_[iris["data"]], columns=feature_names)
    x["target"] = iris["target"]

    data_split = [
        DataSplit(label="train", column_value=0, column_name="eval_flg"),
        DataSplit(label="test", column_value=1, column_name="eval_flg"),
    ]

    return PolarsData(
        data=pl.from_pandas(data=x),
        data_splits=data_split,
    )


@pytest.fixture
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
def sklearn_pipeline() -> tuple[SklearnModel, PandasData]:
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

    return SklearnModel(model=pipe, sample_data=train_data), PandasData(data=train_data)


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


@pytest.fixture
def xgb_df_regressor(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = XGBRegressor(n_estimators=5, max_depth=3)
    reg.fit(X_train.to_numpy(), y_train)
    return reg, X_train[:100]


@pytest.fixture
def random_forest_classifier(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X_train.to_numpy(), y_train)

    return SklearnModel(
        model=reg,
        sample_data=X_train[:100],
        task_type="classification",
        preprocessor=StandardScaler(),
    )


@pytest.fixture
def lgb_classifier(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = lgb.LGBMClassifier(
        n_estimators=3,
        max_depth=3,
        num_leaves=5,
    )
    reg.fit(X_train.to_numpy(), y_train)
    return reg, X_train[:100]


@pytest.fixture
def lgb_classifier_calibrated(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = lgb.LGBMClassifier(
        n_estimators=3,
        max_depth=3,
        num_leaves=5,
    )
    reg.fit(X_train.to_numpy(), y_train)

    calibrated_model = CalibratedClassifierCV(reg, method="isotonic", cv="prefit")
    calibrated_model.fit(X_test, y_test)

    return calibrated_model, X_test[:10]


@pytest.fixture
def lgb_classifier_calibrated_pipeline(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = lgb.LGBMClassifier(
        n_estimators=3,
        max_depth=3,
        num_leaves=5,
    )

    pipe = Pipeline([("preprocess", StandardScaler()), ("clf", CalibratedClassifierCV(reg, method="isotonic", cv=3))])
    pipe.fit(X_train, y_train)

    return pipe, X_test[:10]


@pytest.fixture
def lgb_regressor_model(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = lgb.LGBMRegressor(n_estimators=3, max_depth=3, num_leaves=5)
    reg.fit(X_train.to_numpy(), y_train)

    return LightGBMModel(
        model=reg,
        sample_data=X_train[:100],
        preprocessor=StandardScaler(),
    )


@pytest.fixture
def lgb_booster_model(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
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
        params,
        lgb_train,
        num_boost_round=20,
        valid_sets=lgb_eval,
        callbacks=[
            lgb.early_stopping(stopping_rounds=5),
        ],
    )

    return LightGBMModel(
        model=gbm,
        sample_data=X_train[:100],
        preprocessor=StandardScaler(),
    )


@pytest.fixture(scope="module")
def linear_regression_polars(regression_data_polars: pl.DataFrame) -> Tuple[SklearnModel, PolarsData]:
    data: pl.DataFrame = regression_data_polars

    X = data.select(pl.col(["col_0", "col_1"]))
    y = data.select(pl.col("y"))

    reg = linear_model.LinearRegression().fit(
        X.to_numpy(),
        y.to_numpy(),
    )
    return SklearnModel(model=reg, sample_data=X.to_numpy()), PolarsData(data=X)


@pytest.fixture(scope="module")
def linear_regression(regression_data) -> Tuple[SklearnModel, NumpyData]:
    X, y = regression_data
    reg = linear_model.LinearRegression().fit(X, y)
    return SklearnModel(model=reg, sample_data=X), NumpyData(data=X)


@pytest.fixture
def test_model_card(sklearn_pipeline):
    model, data = sklearn_pipeline
    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        version="1.0.0",
    )
    return model_card


################################################################

### API mocks

#################################################################


@pytest.fixture
def linear_reg_api_example():
    return 6.0, {"inputs": [1, 1]}


@pytest.fixture
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


@pytest.fixture(scope="module")
def huggingface_whisper():
    import transformers

    model = transformers.WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
    model.config.forced_decoder_ids = None

    # come up with some dummy test data to fake out training.
    data = joblib.load("tests/assets/whisper-data.joblib")

    return model, data


@pytest.fixture(scope="module")
def huggingface_openai_gpt():
    from transformers import OpenAIGPTLMHeadModel, OpenAIGPTTokenizer

    tokenizer = OpenAIGPTTokenizer.from_pretrained("openai-gpt")
    model = OpenAIGPTLMHeadModel.from_pretrained("openai-gpt")
    inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")

    return model, inputs


@pytest.fixture(scope="module")
def huggingface_bart() -> HuggingFaceModel:
    from transformers import BartModel, BartTokenizer

    tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
    model = BartModel.from_pretrained("facebook/bart-base")
    inputs = tokenizer(["Hello. How are you"], return_tensors="pt")

    model = HuggingFaceModel(
        model=model,
        preprocessor=tokenizer,
        sample_data=inputs,
        task_type=HuggingFaceTask.TEXT_CLASSIFICATION.value,
    )

    return model


@pytest.fixture(scope="module")
def huggingface_text_classification_pipeline():
    from transformers import pipeline

    pipe = pipeline("text-classification")
    data = "This restaurant is awesome"

    model = HuggingFaceModel(
        model=pipe,
        sample_data=data,
        task_type=HuggingFaceTask.TEXT_CLASSIFICATION.value,
        is_pipeline=True,
    )

    return model


@pytest.fixture(scope="module")
def huggingface_tf_distilbert() -> HuggingFaceModel:
    from optimum.onnxruntime.configuration import AutoQuantizationConfig
    from transformers import AutoTokenizer, TFDistilBertForSequenceClassification

    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model = TFDistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
    inputs = tokenizer(["Hello, my dog is cute", "Hello, my dog is cute"], return_tensors="tf")

    model = HuggingFaceModel(
        model=model,
        preprocessor=tokenizer,
        sample_data=inputs,
        task_type=HuggingFaceTask.TEXT_CLASSIFICATION.value,
        onnx_args=HuggingFaceOnnxArgs(
            ort_type=HuggingFaceORTModel.ORT_MODEL_FOR_SEQUENCE_CLASSIFICATION.value,
            quantize=True,
            config=AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False),
        ),
    )

    return model


@pytest.fixture(scope="module")
def huggingface_torch_distilbert() -> HuggingFaceModel:
    from optimum.onnxruntime.configuration import AutoQuantizationConfig
    from transformers import AutoTokenizer, DistilBertForSequenceClassification

    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
    inputs = tokenizer(["Hello, my dog is cute", "Hello, my dog is cute"], return_tensors="pt")

    model = HuggingFaceModel(
        model=model,
        preprocessor=tokenizer,
        sample_data=inputs,
        task_type=HuggingFaceTask.TEXT_CLASSIFICATION.value,
        onnx_args=HuggingFaceOnnxArgs(
            ort_type=HuggingFaceORTModel.ORT_MODEL_FOR_SEQUENCE_CLASSIFICATION.value,
            quantize=True,
            config=AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False),
        ),
    )

    return model


@pytest.fixture(scope="module")
def huggingface_vit():
    from PIL import Image
    from transformers import ViTFeatureExtractor, ViTModel

    image = Image.open("tests/assets/cats.jpg")

    feature_extractor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224-in21k")
    model = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")

    inputs = feature_extractor(images=image, return_tensors="pt")

    model = HuggingFaceModel(
        model=model,
        preprocessor=feature_extractor,
        sample_data=inputs,
        task_type=HuggingFaceTask.IMAGE_CLASSIFICATION.value,
    )

    return model


@pytest.fixture
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


@pytest.fixture
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
def hist_booster_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = ensemble.HistGradientBoostingRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def huber_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.HuberRegressor(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def knn_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = neighbors.KNeighborsRegressor(n_neighbors=2).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def knn_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf = neighbors.KNeighborsClassifier(n_neighbors=2).fit(X_train, y_train)
    return clf, X_train


@pytest.fixture(scope="module")
def lars_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Lars().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lars_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LarsCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Lasso().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_lars_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoLars().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_lars_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoLarsCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def lasso_lars_ic_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoLarsIC().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def linear_svc(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.LinearSVC(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def linear_svr(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.LinearSVR(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def logistic_regression_cv(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LogisticRegressionCV(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def mlp_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = neural_network.MLPClassifier(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def mlp_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
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
def nu_svc(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.NuSVC(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def nu_svr(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.NuSVR(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def pls_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = cross_decomposition.PLSRegression(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def passive_aggressive_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.PassiveAggressiveClassifier(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def passive_aggressive_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.PassiveAggressiveRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def perceptron(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Perceptron(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def poisson_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.PoissonRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def quantile_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.QuantileRegressor(solver="highs").fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ransac_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.RANSACRegressor(max_trials=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def radius_neighbors_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = neighbors.RadiusNeighborsRegressor().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def radius_neighbors_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf = neighbors.RadiusNeighborsClassifier().fit(X_train, y_train)
    return clf, X_train


@pytest.fixture(scope="module")
def ridge_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Ridge().fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ridge_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.RidgeCV(cv=2).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ridge_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.RidgeClassifier(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def ridge_cv_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.RidgeClassifierCV(cv=2).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def sgd_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.SGDClassifier(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def sgd_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.SGDRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def svc(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.SVC(max_iter=10).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def svr(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
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
def theilsen_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.TheilSenRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def tweedie_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.TweedieRegressor(max_iter=5).fit(X_train, y_train)
    return reg, X_train


@pytest.fixture(scope="module")
def voting_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf1 = linear_model.LogisticRegression(multi_class="multinomial", max_iter=5)
    clf2 = ensemble.RandomForestClassifier(n_estimators=5, random_state=1)
    clf3 = naive_bayes.GaussianNB()
    eclf1 = ensemble.VotingClassifier(
        estimators=[("lr", clf1), ("rf", clf2), ("gnb", clf3)], voting="hard", flatten_transform=False
    )
    eclf1 = eclf1.fit(X_train, y_train)
    return eclf1, X_train


@pytest.fixture(scope="module")
def voting_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf1 = linear_model.LinearRegression()
    clf2 = ensemble.RandomForestRegressor(n_estimators=5, random_state=1)
    clf3 = linear_model.Lasso()
    eclf1 = ensemble.VotingRegressor(estimators=[("lr", clf1), ("rf", clf2), ("lso", clf3)])
    eclf1 = eclf1.fit(X_train, y_train)
    return eclf1, X_train


@pytest.fixture(scope="module")
def deeplabv3_resnet50():
    import torch
    from PIL import Image
    from torchvision import transforms

    model = torch.hub.load("pytorch/vision:v0.8.0", "deeplabv3_resnet50", pretrained=True)
    model.eval()

    input_image = Image.open("tests/assets/deeplab.jpg")
    preprocess = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)

    return PyTorchModel(model=model, sample_data=input_batch)


@pytest.fixture(scope="module")
def pytorch_lightning_model():
    # define any number of nn.Modules (or use your current ones)
    nn.Sequential(nn.Linear(28 * 28, 64), nn.ReLU(), nn.Linear(64, 3))
    nn.Sequential(nn.Linear(3, 64), nn.ReLU(), nn.Linear(64, 28 * 28))

    # define the LightningModule
    class SimpleModel(L.LightningModule):
        def __init__(self):
            super().__init__()
            self.l1 = torch.nn.Linear(in_features=64, out_features=4)

        def forward(self, x):
            return torch.relu(self.l1(x.view(x.size(0), -1)))

    trainer = L.Trainer()
    model = SimpleModel()

    # set model
    trainer.strategy.model = model
    input_sample = torch.randn((1, 64))
    return LightningModel(model=trainer, sample_data=input_sample)


@pytest.fixture(scope="module")
def lightning_regression():
    class SimpleDataset(Dataset):
        def __init__(self):
            X = np.arange(10000)
            y = X * 2
            X = [[_] for _ in X]
            y = [[_] for _ in y]
            self.X = torch.Tensor(X)
            self.y = torch.Tensor(y)

        def __len__(self):
            return len(self.y)

        def __getitem__(self, idx):
            return {"X": self.X[idx], "y": self.y[idx]}

    class MyModel(L.LightningModule):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(1, 1)
            self.criterion = MSELoss()

        def forward(self, inputs_id, labels=None):
            outputs = self.fc(inputs_id)
            return outputs

        def train_dataloader(self):
            dataset = SimpleDataset()
            return DataLoader(dataset, batch_size=1000)

        def training_step(self, batch, batch_idx):
            input_ids = batch["X"]
            labels = batch["y"]
            outputs = self(input_ids, labels)
            loss = 0
            if labels is not None:
                loss = self.criterion(outputs, labels)
            return {"loss": loss}

        def configure_optimizers(self):
            optimizer = Adam(self.parameters())
            return optimizer

    model = MyModel()
    trainer = L.Trainer(max_epochs=1)
    trainer.fit(model)

    X = torch.Tensor([[1.0], [51.0], [89.0]])

    return LightningModel(model=trainer, sample_data=X), MyModel
