import os
from typing import List

import pandas as pd
from pyshipt_logging import ShiptLogging

from .levels import LevelHandler

logger = ShiptLogging.get_logger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))


class Analyzer:
    def __init__(
        self,
        compute_env: str = "gcp",
    ):
        self.compute_env = compute_env

    def run_analysis(
        self,
        ids: List[str],
        checkout_predictions: List[float] = None,
        delivery_predictions: List[float] = None,
        pick_predictions: List[float] = None,
        drop_predictions: List[float] = None,
        drive_predictions: List[float] = None,
        wait_predictions: List[float] = None,
        analysis_type: str = "pay",
        analysis_level: str = "order",
        outlier_removal: bool = True,
        metro_level: bool = False,
        schema: str = "data_science",
    ) -> pd.DataFrame:

        """
        Helper method to run automated pay and arror analysis.
        Given a list of ids (either time bundle id or ng order id)
        along with predictions for various objectives and analysis
        types specificaiton, a query will be run against verified
        actuals and return a dataframe that contains a pay or error
        analysis.

        Args:
            ids: List of time_bundle ids or ng_order ids. If running
            error analysis, time_bundle_ids are required.
            checkout_predictions: List of checkout predictions.
            delivery_predictions: List of delivery predictions.
            pick_predictions: List of pick predictions.
            drop_predictions: List of drop predictions.
            drive_predictions: List of drive predictions.
            wait_predictions: List of wait predictions.
            analysis_type: Whether to run "pay" or "error"
            analysis.
            analysis_level: Whether to run "order" or "bundle"
            level analysis.
            outlier_removal: Whether to remove outliers (True or False).
            Outliers are only used in pay analysis. If running error analysis
            make sure to remove outlier prior to submitting.
            metro_level: Whether to run analysis at metro level or not.
            schema: Snowflake schema to save temporary table to.

        Returns:
            df (pd.Dataframe): A pandas dataframe containing results.
        """

        msg = f"Running {analysis_type} for {analysis_level} level"
        logger.info(msg)
        for handler in LevelHandler.__subclasses__():
            if handler.match_analysis_type(analysis_level):
                dataframe = handler(self.compute_env).run_analysis(
                    ids=ids,
                    checkout_predictions=checkout_predictions,
                    delivery_predictions=delivery_predictions,
                    pick_predictions=pick_predictions,
                    drop_predictions=drop_predictions,
                    drive_predictions=drive_predictions,
                    wait_predictions=wait_predictions,
                    analysis_type=analysis_type,
                    outlier_removal=outlier_removal,
                    schema=schema,
                    metro_level=metro_level,
                )
        return dataframe
