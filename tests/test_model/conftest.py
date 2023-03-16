import pytest
import numpy as np
import joblib
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.ensemble import StackingRegressor
from xgboost import XGBRegressor
import lightgbm as lgb


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


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="module")
def linear_regression():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    reg = LinearRegression().fit(X, y)
    return reg, X
