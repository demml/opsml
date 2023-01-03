import os

import numpy as np
import pandas as pd
import pytest

from opsml_data.connector import SnowflakeQueryRunner
from opsml_data.drift.data_drift import (
    DriftFeatures,
    DriftDetectorData,
    FeatureImportanceCalculator,
    FeatureStats,
    FeatureTypes,
    FeatureHistogram,
    DriftDetector,
    DriftReportParser,
    ParsedFeatureDataFrames,
    DriftVisualizer,
)
from opsml_data.drift.visualize import NumericChart, CategoricalChart, AucChart
from opsml_data.drift.models import FeatureImportance, DriftData, FeatureStatsOutput, HistogramOutput
import altair_viewer


@pytest.mark.parametrize("categorical", [None, ["col_10"]])
def test_drift_features(drift_dataframe, categorical):
    X_train, y_train, X_test, y_test = drift_dataframe

    features = DriftFeatures(
        dtypes=dict(X_train.dtypes),
        target_feature="target",
        categorical_features=categorical,
    )
    assert bool(features.feature_list)

    if bool(categorical):
        assert bool(features.categorical_features)
        assert features.set_feature_type("col_10") == FeatureTypes.CATEGORICAL.value

    else:
        assert not bool(features.categorical_features)
        assert features.set_feature_type("col_10") == FeatureTypes.NUMERIC.value


def _test_drift_detector_data(drift_dataframe):
    X_train, y_train = drift_dataframe

    data_holder = DriftDetectorData(
        reference_data=DriftData(X=X_train, y=y_train),
        current_data=DriftData(X=X_train, y=y_train),
    )
    drift_data = data_holder.create_drift_data()
    assert isinstance(drift_data, DriftData)


@pytest.mark.parametrize("categorical", [None, ["col_10"]])
def test_feature_importance(drift_dataframe, categorical):
    X_train, y_train, X_test, y_test = drift_dataframe

    features = DriftFeatures(
        dtypes=dict(X_train.dtypes),
        target_feature="target",
        categorical_features=categorical,
    )

    data_holder = DriftDetectorData(
        reference_data=DriftData(X=X_train, y=y_train),
        current_data=DriftData(X=X_train, y=y_train),
    )

    training_data = data_holder.create_drift_data()
    importance_calc = FeatureImportanceCalculator(
        data=training_data,
        features=features.feature_list,
        target_feature=features.target_feature,
    )

    importances = importance_calc.compute_importance()
    assert isinstance(importances["col_0"], FeatureImportance)


@pytest.mark.parametrize("feature_type", [0, 1])
def test_feature_stats(drift_dataframe, feature_type):
    X_train, y_train, X_test, y_test = drift_dataframe

    test_data = X_train["col_1"].to_numpy().reshape(-1, 1)

    stats = FeatureStats(
        data=test_data,
        feature_type=feature_type,
        target_val=0,
    )

    nbr_missing, percent_missing = stats.count_missing()

    assert isinstance(nbr_missing, int)
    assert isinstance(percent_missing, float)

    feature_outputs = stats.compute_stats()

    assert isinstance(feature_outputs, FeatureStatsOutput)


@pytest.mark.parametrize("feature_type", [0, 1])
def test_histogram(drift_dataframe, feature_type):
    X_train, y_train, X_test, y_test = drift_dataframe

    data = X_train["col_1"].to_numpy().reshape(-1, 1)
    hist_output = FeatureHistogram(feature_type=feature_type, bins=20).compute_feature_histogram(data=data)
    assert isinstance(hist_output, HistogramOutput)


@pytest.mark.parametrize("categorical", [["col_10"]])
def test_drift_detector(drift_dataframe, categorical):
    X_train, y_train, X_test, y_test = drift_dataframe

    detector = DriftDetector(
        x_reference=X_train,
        y_reference=y_train,
        x_current=X_train,
        y_current=y_train,
        target_feature_name="target",
        categorical_features=categorical,
    )

    importance = detector.importance_calc.compute_importance()
    stats = detector.create_feature_stats()

    assert len(importance.keys()) == len(stats.keys())

    results = detector.run_drift_diagnostics(return_dataframe=True)

    assert isinstance(results, pd.DataFrame)


@pytest.mark.parametrize("categorical", [["col_10"]])
def test_altair_plots(drift_dataframe, categorical):

    X_train, y_train, X_test, y_test = drift_dataframe

    detector = DriftDetector(
        x_reference=X_train,
        y_reference=y_train,
        x_current=X_test,
        y_current=y_test,
        target_feature_name="target",
        categorical_features=categorical,
    )

    detector.run_drift_diagnostics(return_dataframe=False)
    parser = DriftReportParser(drift_report=detector.drift_report)

    parsed_dfs: ParsedFeatureDataFrames = parser.report_to_dataframes()
    df = parsed_dfs.distribution_dataframe

    # test numeric plot
    numeric_data = df.loc[df["feature_type"] == 1]
    numeric_chart = NumericChart(
        data=numeric_data,
        x_column="bins",
        y_column="values",
        color_column="label",
        dropdown_field_name="feature",
    )
    chart = numeric_chart.build_chart(chart_title="Numeric Data")
    chart.save("numeric_chart.html")
    assert os.path.isfile("numeric_chart.html")

    # test categorical
    categorical_data = df.loc[df["feature_type"] == 0]
    categorical_data["bins"] = categorical_data["bins"].astype("int")

    cat_chart = CategoricalChart(
        data=categorical_data,
        x_column="bins",
        y_column="values",
        color_column="label",
        dropdown_field_name="feature",
    )

    chart = cat_chart.build_chart(chart_title="Categorical")
    chart.save("categorical_chart.html")
    assert os.path.isfile("categorical_chart.html")

    importance_data = parsed_dfs.importance_dataframe

    importance_chart = AucChart(
        data=importance_data,
        x_column="auc",
        y_column="feature",
    )

    chart = importance_chart.build_chart(chart_title="AUC")
    chart.save("auc_chart.html")
    assert os.path.isfile("auc_chart.html")


@pytest.mark.parametrize("categorical", [["col_10"], None])
def test_drift_visualizer(drift_dataframe, categorical):

    X_train, y_train, X_test, y_test = drift_dataframe

    detector = DriftDetector(
        x_reference=X_train,
        y_reference=y_train,
        x_current=X_test,
        y_current=y_test,
        target_feature_name="target",
        categorical_features=categorical,
    )
    detector.run_drift_diagnostics(return_dataframe=False)

    visualizer = DriftVisualizer(drift_report=detector.drift_report)
    chart = visualizer.visualize_report()

    # try drift detector by itself
    chart = detector.visualize_report()
    assert os.path.isfile("chart.html")


def _test_real_data():

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

    X_train = df.loc[(df["EVAL_FLG"] == 0) & (df["TRAIN_OUTLIER"] == 0)][features]
    X_test = df.loc[df["EVAL_FLG"] == 1][features]

    y_train = X_train.pop("DROP_OFF_TIME").to_numpy().reshape(-1, 1)
    y_test = X_test.pop("DROP_OFF_TIME").to_numpy().reshape(-1, 1)

    detector = DriftDetector(
        x_reference=X_train,
        y_reference=y_train,
        x_current=X_test,
        y_current=y_test,
        target_feature_name="DROP_OFF_TIME",
        categorical_features=None,
    )

    chart = detector.visualize_report()
    altair_viewer.show(chart)
