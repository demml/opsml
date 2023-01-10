import os

import pandas as pd
from pyshipt_logging import ShiptLogging

from opsml_data.analysis.base_analyzer import PayErrorAnalyzer
from opsml_data.analysis.models import AnalysisAttributes
from opsml_data.helpers.settings import settings

logger = ShiptLogging.get_logger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))


class PayErrorAnalysis:
    def __init__(
        self,
        analysis_type: str = "pay",
        analysis_level: str = "order",
        outlier_removal: bool = True,
        metro_level: bool = False,
        compute_env: str = "gcp",
    ):

        """Helper class for running pay and error analysis

        Args:
            analysis_type (str): Whether to run "pay" or "error" analysis.
            analysis_level (str): Whether to run "order" or "bundle" level analysis.
            outlier_removal (str): Whether to remove outliers (True or False).
            Outliers are only used in pay analysis. If running error analysis
            make sure to remove outlier prior to submitting.
            metro_level (str): Whether to run analysis at metro level or not.
        """

        self.compute_env = compute_env
        self.analysis_type = analysis_type
        self.analysis_level = analysis_level
        self.outlier_removal = outlier_removal
        self.metro_level = metro_level

    def create_analysis_attributes(self):
        if self.analysis_level == "bundle":
            return AnalysisAttributes(
                id_col="bundle_id",
                compute_env=self.compute_env,
                analysis_level=self.analysis_level,
                analysis_type=self.analysis_type,
                table_name=f"preds_bundle_{settings.run_id}",
                metro_level=self.metro_level,
                outlier_removal=self.outlier_removal,
            )

        return AnalysisAttributes(
            id_col="ng_order_id",
            compute_env=self.compute_env,
            analysis_level=self.analysis_level,
            analysis_type=self.analysis_type,
            table_name=f"preds_order_{settings.run_id}",
            metro_level=self.metro_level,
            outlier_removal=self.outlier_removal,
        )

    def run_analysis(
        self,
        prediction_dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        """
        Helper method to run automated pay and arror analysis.
        Takes a pandas dataframe of order/bundle ids along with
        predictions and run pay or error analysis as defined by instance
        attributes.

        Args:
            prediction_dataframe (pd.DataFrame): DataFrame of model predictions

        Returns:
            A pandas dataframe containing results.
        """

        logger.info("Running %s for %s level", self.analysis_type, self.analysis_level)
        analysis_attributes = self.create_analysis_attributes()
        pay_analyzer = PayErrorAnalyzer(
            prediction_dataframe=prediction_dataframe,
            analysis_attributes=analysis_attributes,
        )
        dataframe = pay_analyzer.run_analysis()

        return dataframe
