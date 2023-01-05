from opsml_data.analysis.analyzer import PayErrorAnalysis
from opsml_data.analysis.base_analyzer import FlightPlanSQL, PayErrorAnalyzer
import pandas as pd
import pytest


@pytest.mark.parametrize("compute_env", ["gcp", "local"])
@pytest.mark.parametrize("outlier_removal", [True, False])
@pytest.mark.parametrize("analysis_level", ["order", "bundle"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
def test_sql_getters(compute_env, outlier_removal, analysis_level, analysis_type):

    pay_error_analysis = PayErrorAnalysis(
        analysis_type=analysis_type,
        analysis_level=analysis_level,
        outlier_removal=outlier_removal,
        compute_env=compute_env,
    )

    attributes = pay_error_analysis.create_analysis_attributes()

    sql_getter = next(
        (
            sql
            for sql in FlightPlanSQL.__subclasses__()
            if sql.validate(
                analysis_type=attributes.analysis_type,
            )
        ),
        None,
    )

    sql_str = sql_getter(analysis_attributes=attributes).get_sql()
    assert isinstance(sql_str, str)

    # assert isinstance(query, str)


@pytest.mark.parametrize("compute_env", ["gcp", "local"])
@pytest.mark.parametrize("outlier_removal", [True, False])
@pytest.mark.parametrize("analysis_level", ["order"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
def test_order_analysis_df(
    compute_env,
    outlier_removal,
    analysis_level,
    analysis_type,
    pick_predictions,
):
    order_ids, pick_predictions = pick_predictions

    pay_error_analysis = PayErrorAnalysis(
        analysis_type=analysis_type,
        analysis_level=analysis_level,
        outlier_removal=outlier_removal,
        compute_env=compute_env,
    )

    prediction_dataframe = pd.DataFrame.from_dict(
        {
            "ids": order_ids,
            "pick_predictions": pick_predictions,
        }
    )

    attributes = pay_error_analysis.create_analysis_attributes()

    pay_error_analyzer = PayErrorAnalyzer(
        prediction_dataframe=prediction_dataframe,
        analysis_attributes=attributes,
    )

    dataframe = pay_error_analyzer.create_pred_dataframe()
    assert isinstance(dataframe, pd.DataFrame)


@pytest.mark.parametrize("compute_env", ["gcp", "local"])
@pytest.mark.parametrize("outlier_removal", [True, False])
@pytest.mark.parametrize("analysis_level", ["bundle"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
def test_bundle_analysis_df(
    compute_env,
    outlier_removal,
    analysis_level,
    analysis_type,
    pick_predictions,
):
    order_ids, pick_predictions = pick_predictions

    pay_error_analysis = PayErrorAnalysis(
        analysis_type=analysis_type,
        analysis_level=analysis_level,
        outlier_removal=outlier_removal,
        compute_env=compute_env,
    )

    prediction_dataframe = pd.DataFrame.from_dict(
        {
            "ids": order_ids,
            "pick_predictions": pick_predictions,
        }
    )

    attributes = pay_error_analysis.create_analysis_attributes()

    pay_error_analyzer = PayErrorAnalyzer(
        prediction_dataframe=prediction_dataframe,
        analysis_attributes=attributes,
    )

    dataframe = pay_error_analyzer.create_pred_dataframe()
    assert isinstance(dataframe, pd.DataFrame)


@pytest.mark.parametrize("compute_env", ["local"])
@pytest.mark.parametrize("outlier_removal", [False, True])
@pytest.mark.parametrize("analysis_level", ["bundle", "order"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
@pytest.mark.parametrize("metro_level", [True, False])
def test_analysis_local(
    compute_env,
    outlier_removal,
    analysis_level,
    analysis_type,
    pick_predictions,
    metro_level,
):
    order_ids, pick_predictions = pick_predictions

    pay_error_analysis = PayErrorAnalysis(
        analysis_type=analysis_type,
        analysis_level=analysis_level,
        outlier_removal=outlier_removal,
        compute_env=compute_env,
        metro_level=metro_level,
    )

    prediction_dataframe = pd.DataFrame.from_dict(
        {
            "ids": order_ids,
            "pick_predictions": pick_predictions,
        }
    )

    results = pay_error_analysis.run_analysis(
        prediction_dataframe=prediction_dataframe,
    )

    assert isinstance(results, pd.DataFrame)


@pytest.mark.parametrize("compute_env", ["gcp"])
@pytest.mark.parametrize("outlier_removal", [False])
@pytest.mark.parametrize("analysis_level", ["order"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
def test_analysis_gcp(
    compute_env,
    outlier_removal,
    analysis_level,
    analysis_type,
    pick_predictions,
):
    order_ids, pick_predictions = pick_predictions

    pay_error_analysis = PayErrorAnalysis(
        analysis_type=analysis_type,
        analysis_level=analysis_level,
        outlier_removal=outlier_removal,
        compute_env=compute_env,
    )

    prediction_dataframe = pd.DataFrame.from_dict(
        {
            "ids": order_ids,
            "pick_predictions": pick_predictions,
        }
    )

    results = pay_error_analysis.run_analysis(
        prediction_dataframe=prediction_dataframe,
    )

    assert isinstance(results, pd.DataFrame)
