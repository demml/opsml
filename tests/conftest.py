import os
from sqlalchemy import create_engine

# from opsml_artifacts.helpers.settings import SnowflakeParams
from opsml_artifacts.registry.sql.sql_schema import DataSchema, ModelSchema, ExperimentSchema, PipelineSchema
from opsml_artifacts.registry.sql.registry import CardRegistry
from opsml_artifacts.helpers.gcp_utils import GCPMLScheduler, GCSStorageClient
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import sessionmaker
import numpy as np
import pandas as pd
import pyarrow as pa

from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.ensemble import StackingRegressor
import lightgbm as lgb
import joblib
from pydantic import BaseModel


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


# @pytest.fixture(scope="session")
# def test_settings():
#    from opsml_artifacts.helpers.settings import settings
#
#    return settings


@pytest.fixture(scope="function")
def fake_snowflake_params():
    return SnowflakeParams(
        username="test",
        password="test",
        host="host",
        database="test",
        warehouse="test",
        role="test",
    )


@pytest.fixture(scope="function")
def db_registries():

    url = "sqlite:///:memory:"
    execution_options = {"schema_translate_map": {"ds-artifact-registry": None}}
    engine = create_engine(url=url, execution_options=execution_options)
    mock_session = sessionmaker(bind=engine)
    with patch.multiple(
        "opsml_artifacts.registry.sql.sql_schema.SqlManager",
        _sql_session=mock_session,
        _create_table=MagicMock(return_value=True),
    ):

        DataSchema.__table__.create(bind=engine, checkfirst=True)
        ModelSchema.__table__.create(bind=engine, checkfirst=True)
        ExperimentSchema.__table__.create(bind=engine, checkfirst=True)
        PipelineSchema.__table__.create(bind=engine, checkfirst=True)

        model_registry = CardRegistry(registry_name="model")
        data_registry = CardRegistry(registry_name="data")
        experiment_registry = CardRegistry(registry_name="experiment")
        pipeline_registry = CardRegistry(registry_name="pipeline")

        yield {
            "data": data_registry,
            "model": model_registry,
            "experiment": experiment_registry,
            "pipeline": pipeline_registry,
        }

        # drop tables
        ModelSchema.__table__.drop(bind=engine, checkfirst=True)
        DataSchema.__table__.drop(bind=engine, checkfirst=True)
        ExperimentSchema.__table__.drop(bind=engine, checkfirst=True)
        PipelineSchema.__table__.drop(bind=engine, checkfirst=True)


##### Mocked classes as fixtures


@pytest.fixture()
def test_query():
    query = "SELECT ORDER_ID FROM PRD_DATALAKEHOUSE.DATA_SCIENCE.ORDER_STATS limit 100"

    return query


@pytest.fixture(scope="session", autouse=True)
def mock_gcsfs():
    with patch.multiple(
        "gcsfs.GCSFileSystem",
        ls=MagicMock(return_value=["gs://test"]),
        upload=MagicMock(return_value=True),
        download=MagicMock(return_value=True),
    ) as mocked_gcsfs:
        yield mocked_gcsfs


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


@pytest.fixture(scope="function")
def mock_snowflake_query_runner(test_df):
    with patch.multiple(
        "opsml_artifacts.connector.snowflake.SnowflakeQueryRunner",
        submit_query=MagicMock(return_value=(200, "mock")),
        poll_results=MagicMock(return_value=None),
        query_status=MagicMock(return_value={"query_status": "success"}),
        results_to_gcs=MagicMock(return_value=None),
        gcs_to_parquet=MagicMock(return_value=test_df),
        _set_local_database=MagicMock(return_value=None),
        run_local_query=MagicMock(return_value=test_df),
    ) as mock_runner:

        yield mock_runner


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

    with patch("opsml_artifacts.helpers.gcp_utils.GCSStorageClient", MockStorage) as mock_storage:

        yield mock_storage


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

    with patch("opsml_artifacts.helpers.gcp_utils.GCPMLScheduler", MockScheduler) as mock_scheduler:

        yield mock_scheduler


######## Data for registry tests
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


################################### MODELS ###################################
@pytest.fixture(scope="module")
def linear_regression():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    reg = LinearRegression().fit(X, y)
    return reg, X


@pytest.fixture(scope="function")
def model_list():

    models = []

    for model in [LinearRegression, lgb.LGBMRegressor, XGBRegressor]:
        X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        y = np.dot(X, np.array([1, 2])) + 3
        reg = model().fit(X, y)
        models.append(reg)

    estimators = [("lr", RandomForestRegressor()), ("svr", XGBRegressor())]

    reg = StackingRegressor(
        estimators=estimators,
        final_estimator=RandomForestRegressor(n_estimators=10, random_state=42),
        cv=2,
    )

    reg.fit(X, y)
    models.append(reg)

    return models, X


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


@pytest.fixture(scope="function")
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
