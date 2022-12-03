import os
import time
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from opsml_data.analysis.levels import LevelHandler
from opsml_data.analysis.helpers import Analyzer
from opsml_data.connector.snowflake import SnowflakeDataGetter
from opsml_data.connector.base import GCPQueryRunner
from opsml_data.helpers.defaults import params


@pytest.mark.parametrize("id_col", ["ng_order_id", "bundle_id"])
@pytest.mark.parametrize("compute_env", ["gcp", "local"])
def test_handler(id_col, compute_env):
    handler = LevelHandler(id_col=id_col, compute_env=compute_env)

    if compute_env == "gcp":
        assert handler.data_getter is not None
        assert handler.storage_client is not None


@pytest.mark.parametrize("id_col", ["ng_order_id", "bundle_id"])
@pytest.mark.parametrize("compute_env", ["gcp", "local"])
@pytest.mark.parametrize("outlier_removal", [True, False])
@pytest.mark.parametrize("analysis_level", ["order", "bundle"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
def test_handler_sql_template(id_col, compute_env, outlier_removal, analysis_level, analysis_type):
    handler = LevelHandler(id_col=id_col, compute_env=compute_env)

    query = handler._get_sql_template(
        analysis_level=analysis_level,
        analysis_type=analysis_type,
        outlier_removal=outlier_removal,
        metro_level=False,
        table_name="test",
    )

    assert isinstance(query, str)


@pytest.mark.parametrize("id_col", ["ng_order_id", "bundle_id"])
@pytest.mark.parametrize("compute_env", ["gcp", "local"])
def test_handler_get_dataframe(
    id_col,
    compute_env,
    pick_predictions,
):
    order_ids, pick_predictions = pick_predictions
    handler = LevelHandler(id_col=id_col, compute_env=compute_env)

    df = handler._create_pred_dataframe(ids=order_ids, pick_predictions=pick_predictions, id_col=id_col)

    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize("id_col", ["ng_order_id", "bundle_id"])
@pytest.mark.parametrize("compute_env", ["gcp", "local"])
def test_handler_upload_to_gcs(
    id_col,
    compute_env,
    pick_predictions,
    unique_id,
):
    order_ids, pick_predictions = pick_predictions
    handler = LevelHandler(id_col=id_col, compute_env=compute_env)

    df = handler._create_pred_dataframe(ids=order_ids, pick_predictions=pick_predictions, id_col=id_col)

    assert isinstance(df, pd.core.frame.DataFrame)

    if compute_env == "env":
        gcs_uri = handler._upload_dataframe_to_gcs(df, unique_id)

        assert isinstance(
            gcs_uri,
            str,
        )

        os.system(f"gsutil rm {gcs_uri}")


@pytest.mark.parametrize("id_col", ["ng_order_id"])
@pytest.mark.parametrize("compute_env", ["gcp"])
def test_handler_gcs_to_table(
    id_col,
    compute_env,
    pick_predictions,
    unique_id,
):
    order_ids, pick_predictions = pick_predictions
    handler = LevelHandler(id_col=id_col, compute_env=compute_env)

    df = handler._create_pred_dataframe(ids=order_ids, pick_predictions=pick_predictions, id_col=id_col)

    assert isinstance(df, pd.core.frame.DataFrame)

    gcs_url = handler._upload_dataframe_to_gcs(df, unique_id)

    assert isinstance(
        gcs_url,
        str,
    )

    handler._gcs_to_table(gcs_url, f"preds_{unique_id}")

    # delete everything
    os.system(f"gsutil rm {gcs_url}")
    query_runner = GCPQueryRunner(
        snowflake_api_auth=params.snowflake_api_auth,
        snowflake_api_url=params.snowflake_api_url,
    )
    response = query_runner.submit_query(
        query=f"DROP TABLE DATA_SCIENCE.preds_{unique_id};",
        to_storage=False,
    )
    assert response.gcs_url == None


@pytest.mark.parametrize("compute_env", ["local"])
@pytest.mark.parametrize("analysis_level", ["order", "bundle"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
def test_handler_local_run_analysis(
    compute_env,
    pick_predictions,
    unique_id,
    analysis_type,
    analysis_level,
    sf_schema,
    df_columns,
):
    order_ids, pick_predictions = pick_predictions
    if analysis_level == "order":
        id_col = "ng_order_id"
    else:
        id_col = "bundle_id"

    with patch.object(LevelHandler, "_run_analysis") as _run_analysis:
        _run_analysis.return_value = pd.DataFrame(
            np.empty((10, 7)) * np.nan,
            columns=df_columns,
        )

        handler = LevelHandler(id_col=id_col, compute_env=compute_env)

        df = handler._run_analysis(
            ids=order_ids,
            pick_predictions=pick_predictions,
            analysis_type=analysis_type,
            analysis_level=analysis_level,
            table_name=f"preds_{analysis_level}_{unique_id}",
            schema=sf_schema,
        )

        assert isinstance(df, pd.core.frame.DataFrame)


@pytest.mark.parametrize("compute_env", ["local"])
@pytest.mark.parametrize("analysis_level", ["bundle", "order"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
@pytest.mark.parametrize("metro_level", [True, False])
@pytest.mark.parametrize("outlier_removal", [True, False])
def test_analyzer(
    compute_env,
    pick_predictions,
    analysis_type,
    analysis_level,
    df_columns,
    metro_level,
    outlier_removal,
):
    order_ids, pick_predictions = pick_predictions
    with patch.object(Analyzer, "run_analysis") as run_analysis:
        run_analysis.return_value = pd.DataFrame(
            np.empty((10, 7)) * np.nan,
            columns=df_columns,
        )

        analyzer = Analyzer(compute_env == compute_env)

        df = analyzer.run_analysis(
            ids=order_ids,
            pick_predictions=pick_predictions,
            analysis_type=analysis_type,
            analysis_level=analysis_level,
            metro_level=metro_level,
            outlier_removal=outlier_removal,
        )

        assert isinstance(df, pd.core.frame.DataFrame)


# limiting options because these queries take a while
@pytest.mark.parametrize("compute_env", ["gcp"])
@pytest.mark.parametrize("analysis_type", ["error"])
@pytest.mark.parametrize("metro_level", [False])
@pytest.mark.parametrize("outlier_removal", [False])
def test_bundle_run(
    compute_env,
    analysis_type,
    metro_level,
    outlier_removal,
    bundle_query,
):

    data_getter = SnowflakeDataGetter()
    data = data_getter.get_data(query=bundle_query)

    analyzer = Analyzer(compute_env=compute_env)

    df = analyzer.run_analysis(
        ids=data["TIME_BUNDLE_ID"],
        drop_predictions=data["DROP_TIME"],
        analysis_type=analysis_type,
        analysis_level="bundle",
        metro_level=metro_level,
        outlier_removal=outlier_removal,
    )

    assert isinstance(df, pd.core.frame.DataFrame)


@pytest.mark.parametrize("compute_env", ["gcp"])
@pytest.mark.parametrize("analysis_type", ["pay", "error"])
@pytest.mark.parametrize("metro_level", [True, False])
@pytest.mark.parametrize("outlier_removal", [True, False])
def test_order_run(
    compute_env,
    analysis_type,
    metro_level,
    outlier_removal,
    order_query,
):

    data_getter = SnowflakeDataGetter()
    data = data_getter.get_data(query=order_query)

    analyzer = Analyzer(compute_env=compute_env)

    df = analyzer.run_analysis(
        ids=data["NG_ORDER_ID"],
        drop_predictions=data["DROP_TIME"],
        analysis_type=analysis_type,
        analysis_level="order",
        metro_level=metro_level,
        outlier_removal=outlier_removal,
    )

    assert isinstance(df, pd.core.frame.DataFrame)
