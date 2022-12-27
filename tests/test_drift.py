import os

import numpy as np
import pandas as pd
import pytest

from opsml_data.connector import SnowflakeQueryRunner
from opsml_data.drift import Drifter


def test_intersection():
    mu_1 = -4  # mean of the first distribution
    mu_2 = 4  # mean of the second distribution
    data_1 = np.random.normal(mu_1, 2.0, 1000)
    data_2 = np.random.normal(mu_2, 2.0, 1000)

    hist1, edge1 = np.histogram(
        data_1,
        density=False,
    )
    hist2, edge2 = np.histogram(
        data_2,
        bins=edge1,
        density=False,
    )

    drifter = Drifter()
    intersection = drifter._compute_intersection(hist2, hist1)
    assert isinstance(intersection, float)


@pytest.mark.parametrize("feature_type", ["numerical", "categorical"])
def test_feature_drift(feature_type):
    mu_1 = -4  # mean of the first distribution
    mu_2 = 4  # mean of the second distribution
    data_1 = np.random.normal(mu_1, 2.0, 1000)
    data_2 = np.random.normal(mu_2, 2.0, 1000)

    drifter = Drifter()
    results = drifter._compute_feature_stats(
        data_1,
        data_2,
        "reference",
        "current",
        feature_type,
    )
    assert isinstance(results, dict)


def test_feature_importance_drift():
    mu_1 = -4  # mean of the first distribution
    mu_2 = 4  # mean of the second distribution
    X_train = np.random.normal(mu_1, 2.0, size=(1000, 10))
    X_test = np.random.normal(mu_2, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X_train = pd.DataFrame(X_train, columns=col_names)
    X_train["target_feature"] = np.random.randint(1, 100, size=(1000, 1))

    X_test = pd.DataFrame(X_test, columns=col_names)
    X_test["target_feature"] = np.random.randint(5, 50, size=(1000, 1))

    drifter = Drifter()
    results = drifter._compute_drift_feature_importance(X_train, X_test, col_names, target_feature="target_feature")

    assert isinstance(results, dict)


def test_run_diagnostics():
    mu_1 = -4  # mean of the first distribution
    mu_2 = 4  # mean of the second distribution
    X_train = np.random.normal(mu_1, 2.0, size=(1000, 10))
    X_test = np.random.normal(mu_2, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X_train = pd.DataFrame(X_train, columns=col_names)
    X_train["target_feature"] = np.random.randint(1, 100, size=(1000, 1))

    X_test = pd.DataFrame(X_test, columns=col_names)
    X_test["target_feature"] = np.random.randint(5, 50, size=(1000, 1))

    drifter = Drifter()
    results = drifter.run_drift_diagnostics(
        reference_data=X_train,
        current_data=X_test,
        target_feature="target_feature",
        return_df=True,
    )

    assert isinstance(results, pd.DataFrame)

    results = drifter.run_drift_diagnostics(
        reference_data=X_train,
        current_data=X_test,
        target_feature="target_feature",
        return_df=True,
        exclude_cols=["col_0"],
        categorical_features=["col_2"],
    )

    assert "col_0" not in results["feature"].unique()
    subset = results.loc[results["feature"] == "col_2"]["type"]
    assert subset.values[0] == "categorical"


def test_drift_chart():
    mu_1 = -4  # mean of the first distribution
    mu_2 = 4  # mean of the second distribution
    X_train = np.random.normal(mu_1, 2.0, size=(1000, 10))
    X_test = np.random.normal(mu_2, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X_train = pd.DataFrame(X_train, columns=col_names)
    X_train["target_feature"] = np.random.randint(1, 100, size=(1000, 1))

    X_test = pd.DataFrame(X_test, columns=col_names)
    X_test["target_feature"] = np.random.randint(5, 50, size=(1000, 1))

    drifter = Drifter()
    results = drifter.run_drift_diagnostics(
        reference_data=X_train,
        current_data=X_test,
        target_feature="target_feature",
        return_df=True,
    )

    chart = drifter.chart_drift_diagnostics(df=results)
    os.remove("chart.html")


def test_real_data():

    runner = SnowflakeQueryRunner()
    df = runner.run_query(sql_file="data.sql")
    features = [
        "NBR_ADDRESSES",
        "NBR_ORDERS",
        "NBR_RX",
        "NBR_APT",
        "METRO_X",
        "METRO_Y",
        "METRO_Z",
        "DROP_OFF_TIME",
    ]

    train_data = df.loc[(df["EVAL_FLG"] == 0) & (df["TRAIN_OUTLIER"] == 0)][features]
    eval_data = df.loc[df["EVAL_FLG"] == 1][features]

    drifter = Drifter()
    drift_df = drifter.run_drift_diagnostics(
        reference_data=train_data,
        current_data=eval_data,
        target_feature="DROP_OFF_TIME",
        current_label="eval",
        reference_label="train",
        return_df=True,
    )

    drifter.chart_drift_diagnostics(
        df=drift_df,
        reference_label="train",
        current_label="eval",
    )

    # mu_1 = -4  # mean of the first distribution
    # mu_2 = 4  # mean of the second distribution
    # X_train = np.random.normal(mu_1, 2.0, size=(1000, 10))
    # X_test = np.random.normal(mu_2, 2.0, size=(1000, 10))


#
# col_names = []
# for i in range(0, X_train.shape[1]):
#    col_names.append(f"col_{i}")
#
# X_train = pd.DataFrame(X_train, columns=col_names)
# X_train["target_feature"] = np.random.randint(1, 100, size=(1000, 1))
#
# X_test = pd.DataFrame(X_test, columns=col_names)
# X_test["target_feature"] = np.random.randint(5, 50, size=(1000, 1))
#
# drifter = Drifter()
# results = drifter.run_drift_diagnostics(
#    reference_data=X_train,
#    current_data=X_test,
#    target_feature="target_feature",
#    return_df=True,
# )
#
# chart = drifter.chart_drift_diagnostics(df=results)
# os.remove("chart.html")
