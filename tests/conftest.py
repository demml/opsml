import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

from lightgbm import LGBMRegressor
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor

from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.helpers.utils import FindPath, GCPClient
from opsml_artifacts.registry.cards.connection import create_sql_engine
from opsml_artifacts.registry.cards.registry import CardRegistry
from opsml_artifacts.registry.cards.sql_schema import TestDataSchema, TestModelSchema
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import RidgeCV
import joblib

dir_path = os.path.dirname(os.path.realpath(__file__))
gcs_storage_client = GCPClient.get_service(
    service_name="storage",
    gcp_credentials=settings.gcp_creds,
)


def pytest_sessionfinish(session, exitstatus):
    """whole test run finishes."""
    try:
        os.remove("gcp_key.json")
    except Exception as e:
        pass

    paths = [path for path in Path(os.getcwd()).rglob("*.csv")]
    for path in paths:
        if "pick_time_example.csv" in path.name:
            pass
        else:
            os.remove(path)

    paths = [path for path in Path(os.getcwd()).rglob("*chart.html")]
    if paths:
        for path in paths:
            os.remove(path)

    # delete all test data registry files
    blobs = gcs_storage_client.list_objects(
        gcs_bucket=settings.gcs_bucket,
        prefix="test_data_registry/",
    )

    for blob in blobs:
        gcs_storage_client.delete_object(
            gcs_bucket=settings.gcs_bucket,
            blob_path=blob.name,
        )

    # delete all test model registry files
    blobs = gcs_storage_client.list_objects(
        gcs_bucket=settings.gcs_bucket,
        prefix="test_model_registry/",
    )

    for blob in blobs:
        gcs_storage_client.delete_object(
            gcs_bucket=settings.gcs_bucket,
            blob_path=blob.name,
        )


@pytest.fixture(scope="session")
def test_settings():

    return settings


@pytest.fixture(scope="session")
def mock_response():
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    data = {
        "query_id": None,
        "gcs_url": "gs://py-opsml/data/e8e13de0e2a74f56be89d285fa97aab9.csv",
    }
    response = MockResponse(json_data=data, status_code=200)

    return response


@pytest.fixture(scope="session")
def gcs_url():
    return "gs://py-opsml/data/20220927155229.csv"


@pytest.fixture(scope="session")
def pick_predictions():
    csv_path = FindPath().find_filepath(
        "pick_time_example.csv",
        dir_path,
    )
    df = pd.read_csv(csv_path)
    return df["NG_ORDER_ID"].to_list(), df["PREDICTIONS"].to_list()


@pytest.fixture(scope="session")
def unique_id():
    id_ = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    return id_


@pytest.fixture(scope="session")
def sf_schema():
    return "data_science"


@pytest.fixture(scope="session")
def df_columns():
    return [
        "ng_order_id",
        "checkout_time",
        "delivery_time",
        "pick_time",
        "drop_time",
        "drive_time",
        "wait_time",
    ]


@pytest.fixture(scope="session")
def bundle_query():
    query = """
        SELECT
        TIME_BUNDLE_ID,
        DROP_OFF_TIME/60 AS ACTUAL,
        (NBR_ADDRESSES*3.8531) -0.0415 AS DROP_TIME
        FROM DATA_SCIENCE.OPSML_FP_BUNDLES_TIME_ACTUALS
        WHERE DROP_OFF_EVAL_FLG = 1
        AND DROP_OFF_EVAL_OUTLIER = 0
        """
    return query


@pytest.fixture(scope="session")
def order_query():
    query = """
        SELECT 
        NG_ORDER_ID,
        (3.8531) -0.0415 AS DROP_TIME,
        NULL AS CHECKOUT_TIME,
        NULL AS DELIVERY_TIME,
        NULL AS DRIVE_TIME,
        NULL AS WAIT_TIME,
        NULL AS PICK_TIME
        FROM DATA_SCIENCE.OPSML_FP_ORDERS_TIME_ACTUALS
        WHERE BUNDLE_TYPE = 'TARP'
        AND DROP_OFF_EVAL_FLG = 1
        AND DROP_OFF_EVAL_OUTLIER = 0
        """
    return query


@pytest.fixture()
def test_query():
    query = "SELECT ORDER_ID FROM PRD_DATALAKEHOUSE.DATA_SCIENCE.ORDER_STATS limit 100"

    return query


@pytest.fixture(scope="session")
def test_array():
    data = np.random.rand(10, 100)
    return data


@pytest.fixture(scope="session")
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
def test_split_array():
    indices = np.array([0, 1, 2])
    return [{"label": "train", "indices": indices}]


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
    y_train = np.random.randint(1, 100, size=(1000, 1))
    y_test = np.random.randint(2, 100, size=(1000, 1))

    return X_train, y_train, X_test, y_test


@pytest.fixture(scope="session")
def test_arrow_table():
    n_legs = pa.array([2, 4, 5, 100])
    animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
    names = ["n_legs", "animals"]
    table = pa.Table.from_arrays([n_legs, animals], names=names)
    return table


@pytest.fixture(scope="session")
def setup_data_registry():

    engine = create_sql_engine()
    TestDataSchema.__table__.drop(bind=engine, checkfirst=True)
    TestDataSchema.__table__.create(bind=engine, checkfirst=True)
    registry = CardRegistry(registry_name="data_test")

    yield registry
    TestDataSchema.__table__.drop(bind=engine, checkfirst=True)


@pytest.fixture(scope="session")
def setup_model_registry():

    engine = create_sql_engine()
    TestModelSchema.__table__.drop(bind=engine, checkfirst=True)
    TestModelSchema.__table__.create(bind=engine, checkfirst=True)
    registry = CardRegistry(registry_name="model_test")

    yield registry
    TestModelSchema.__table__.drop(bind=engine, checkfirst=True)


@pytest.fixture(scope="session")
def storage_client():

    return gcs_storage_client


@pytest.fixture(scope="function")
def drift_report():
    drift_report = joblib.load("tests/drift_report.joblib")

    return drift_report


@pytest.fixture(scope="function")
def test_sql_file():
    return "test_drop_off_bundle.sql"


@pytest.fixture(scope="function")
def var_store_order_query():
    return """SELECT NG_ORDER_ID FROM OPSML_FP_ORDERS_TIME_ACTUALS LIMIT 10"""


@pytest.fixture(scope="module")
def linear_regression():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    reg = LinearRegression().fit(X, y)
    return reg, X


@pytest.fixture(scope="function")
def model_list():

    models = []

    for model in [LinearRegression, LGBMRegressor, XGBRegressor]:
        X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        y = np.dot(X, np.array([1, 2])) + 3
        reg = model().fit(X, y)
        models.append(reg)

    estimators = [("lr", RandomForestRegressor()), ("svr", LinearRegression())]

    reg = StackingRegressor(
        estimators=estimators,
        final_estimator=RandomForestRegressor(n_estimators=10, random_state=42),
        cv=2,
    )

    reg.fit(X, y)
    models.append(reg)

    return models, X


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
    pipe = Pipeline([("preprocess", preprocessor), ("rf", RandomForestRegressor())])
    pipe.fit(train_data, data["y"])

    return pipe, train_data
