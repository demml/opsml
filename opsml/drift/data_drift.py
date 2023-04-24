import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import altair as alt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, roc_curve
from sklearn.preprocessing import scale

from opsml.drift.drift_utils import shipt_theme
from opsml.drift.types import (
    ChartType,
    DriftData,
    DriftReport,
    ExtractedAttributes,
    FeatureImportance,
    FeatureStatsOutput,
    FeatureTypes,
    HistogramOutput,
    ParsedFeatureDataFrames,
    ParsedFeatureImportance,
    ParsedFeatures,
)
from opsml.drift.visualize import AltairChart

warnings.simplefilter(action="ignore", category=FutureWarning)  # type: ignore
import pandas as pd  # noqa: E402 #pylint: disable=[wrong-import-position,wrong-import-order]

alt.themes.register("shipt", shipt_theme)
alt.themes.enable("shipt")


class FeatureImportanceCalculator:
    """Provides metrics for drift detections"""

    def __init__(
        self,
        features: List[str],
        data: DriftData,
        target_feature: Optional[str] = None,
    ):
        self.reg = LogisticRegression(max_iter=1000)
        self.features = features
        self.data = data
        self.features_and_target = [*self.features, *[target_feature]]

    def compute_auc(self, x_data: np.ndarray, y_data: np.ndarray) -> float:
        x_tr = scale(x_data)
        self.reg.fit(x_tr, y_data)
        preds = self.reg.predict_proba(x_data)[::, 1]
        fpr, tpr, _ = roc_curve(y_data, preds, pos_label=1)
        return auc(fpr, tpr)

    def calculate_feature_importance(self):
        x_tr = scale(self.data.X)
        self.reg.fit(x_tr, self.data.y)
        coefs = list(self.reg.coef_[0])
        coefs.append(None)  # for target

        return coefs

    def calculate_feature_auc(self):
        feature_aucs = []
        x_data = np.hstack((self.data.X[self.features].to_numpy(), self.data.target))
        for feature in range(x_data.shape[1]):
            computed_auc = self.compute_auc(
                x_data=x_data[:, feature].reshape(-1, 1),
                y_data=self.data.y,
            )
            feature_aucs.append(computed_auc)
        return feature_aucs

    def combine_feature_importance_auc(
        self, feature_importances: List[float], feature_aucs: List[float]
    ) -> Dict[Optional[str], FeatureImportance]:
        feature_dict = {}
        for feature_name, importance, computed_auc in zip(self.features_and_target, feature_importances, feature_aucs):
            feature_dict[feature_name] = FeatureImportance(
                importance=importance,
                auc=computed_auc,
            )

        return feature_dict

    def compute_importance(
        self,
    ) -> Dict[Optional[str], FeatureImportance]:
        """Computes feature importance from object attributes

        Returns
            Dictionary containing features and their importances
        """

        feature_importances = self.calculate_feature_importance()
        feature_aucs = self.calculate_feature_auc()
        combined_features = self.combine_feature_importance_auc(
            feature_importances=feature_importances,
            feature_aucs=feature_aucs,
        )
        return combined_features


class DriftFeatures:
    """Computes relevant feature attributes used in drift detection"""

    def __init__(
        self,
        dtypes: Dict[str, Any],
        categorical_features: List[Optional[str]],
        target_feature: Optional[str] = None,
    ):
        self.dtypes = dtypes
        self.target_feature = target_feature
        self.feature_list = self.create_feature_list()
        self.categorical_features = self.create_categorical_feature_list(
            cat_features=categorical_features,
        )
        # else:
        # self.categorical_features = []

    def create_feature_list(self) -> List[str]:
        feature_mapping = self.get_feature_types()
        return list(feature_mapping.keys())

    def create_categorical_feature_list(self, cat_features: List[Optional[str]]) -> List[Optional[str]]:
        return [feature for feature in self.feature_list if feature in cat_features]

    def get_feature_types(self):
        feature_mapping = {}

        for key, val in self.dtypes.items():
            if val == "O":
                feature_mapping[key] = "str"
            else:
                feature_mapping[key] = str(val)

        return feature_mapping

    def set_feature_type(self, feature: str):
        if feature in self.categorical_features:
            return 0
        return 1


class DriftDetectorData:
    """Houses data used for drift detection"""

    def __init__(
        self,
        reference_data: DriftData,
        current_data: DriftData,
    ):
        self.reference_data = reference_data
        self.current_data = current_data

    def create_y_data(self) -> np.ndarray:
        ref_targets = np.zeros((self.reference_data.y.shape[0],))
        current_targets = np.ones((self.current_data.y.shape[0],))
        y_train = np.hstack((ref_targets, current_targets))

        return y_train

    def create_x_data(self) -> Union[np.ndarray, pd.DataFrame]:
        x_train = pd.concat([self.reference_data.X, self.current_data.X])
        x_train.dropna(inplace=True)

        return x_train

    def create_drift_data(self) -> DriftData:
        x_drift = self.create_x_data()
        y_drift = self.create_y_data()
        target = np.vstack((self.reference_data.y.reshape(-1, 1), self.current_data.y.reshape(-1, 1)))

        return DriftData(X=x_drift, y=y_drift, target=target)


class FeatureHistogram:
    """Creates histogram values and bins for feature data"""

    def __init__(
        self,
        bins: Union[int, List[Union[int, float]]],
        feature_type: int,
    ):
        self.bins = bins
        self.feature_type = feature_type

    def compute_feature_histogram(self, data: np.ndarray) -> HistogramOutput:
        if FeatureTypes(self.feature_type) == FeatureTypes.NUMERIC:
            hist, edges = np.histogram(data, bins=self.bins, density=False)
        else:
            edges, hist = np.unique(data, return_counts=True)
        hist = np.divide(hist, data.shape[0])

        return HistogramOutput(
            values=hist,
            bins=edges,
        )


class FeatureStats:
    """Calculates statistics for single feature data"""

    def __init__(
        self,
        data: np.ndarray,
        feature_type: int,
        target_val: int,
        bins: Optional[Union[int, List[Union[int, float]]]] = None,
    ):
        self.data = data
        self.feature_type = feature_type
        self.target_val = target_val
        self.bins = bins

        if bins is None:
            bins = 20

        self.histogram = FeatureHistogram(
            bins=bins,
            feature_type=self.feature_type,
        )

    @staticmethod
    def compute_intersection(
        current_distribution: HistogramOutput,
        reference_distribution: HistogramOutput,
    ):
        overlap_vals = []
        min_bin = min(reference_distribution.bins)
        max_bin = max(reference_distribution.bins)
        for bin_, val in zip(current_distribution.bins, current_distribution.values):
            if min_bin <= bin_ <= max_bin:
                overlap_vals.append(val)
        intersection = np.sum(overlap_vals)
        return intersection

    def count_missing(self) -> Tuple[int, float]:
        nbr_missing = len(np.argwhere(np.isnan(self.data)))
        percent_missing = round((nbr_missing / self.data.shape[0]) * 100, 2)

        return nbr_missing, percent_missing

    def compute_stats(self) -> FeatureStatsOutput:
        # count number of missing records
        nbr_missing_records, percent_missing = self.count_missing()

        # Remove missing values
        new_data = self.data[~np.isnan(self.data)]
        feature_hist = self.histogram.compute_feature_histogram(data=new_data)
        unique_values = len(np.unique(self.data))

        return FeatureStatsOutput(
            historgram=feature_hist,
            missing_records=f"{nbr_missing_records}, {percent_missing}%",
            unique=unique_values,
            type_=self.feature_type,
            target_feature=self.target_val,
        )


# Detects drift between reference and current dataframe
class DriftDetector:
    def __init__(
        self,
        x_reference: pd.DataFrame,
        y_reference: np.ndarray,
        x_current: pd.DataFrame,
        y_current: np.ndarray,
        dependent_var_name: str,
        categorical_features: Optional[List[Optional[str]]] = None,
    ):
        """Calculates a drift report for reference vs current data

        Args:
            x_reference (pd.DataFrame): Pandas dataframe of reference data for features
            y_reference (np.ndarray): Numpy array of target reference data
            x_current (pd.DataFrame): Pandas dataframe of current data for features
            y_current (np.ndarray): Numpy array of target current data
            target_feature (str): Optional name of target data
            categorical_features (list(str)): Optional list of categorical features
        """

        if categorical_features is None:
            categorical_features = []

        self.drift_features = DriftFeatures(
            dtypes=dict(x_reference.dtypes),
            categorical_features=categorical_features,
            target_feature=dependent_var_name,
        )

        self.drift_data = DriftDetectorData(
            reference_data=DriftData(X=x_reference, y=y_reference),
            current_data=DriftData(X=x_current, y=y_current),
        )

        self.training_data = self.drift_data.create_drift_data()
        self.importance_calc = FeatureImportanceCalculator(
            data=self.training_data,
            features=self.drift_features.feature_list,
            target_feature=self.drift_features.target_feature,
        )
        self.features_and_target = [*self.drift_features.feature_list, *[dependent_var_name]]

    def run_drift_diagnostics(self, return_dataframe: bool = False) -> Union[pd.DataFrame, Dict[str, DriftReport]]:
        """Computes drift diagnostics between reference and current
        data based upon column mapping

        Args:
            return_dataframe (bool): Whether to return a summary dataframe.
            If false, a dictionary of pydantic models will be returned.

        Returns:
            If "return_dataframe" is True, a pandas dataframe of computed drift statistics
            will be returned. If "return_dataframe" is False, a drift report in the form
            of a dictionary of pydantic models will be returned.

            *Note: DataCards only accept the pydantic form of the drift report.
        """

        feature_importance = self.importance_calc.compute_importance()
        feature_stats = self.create_feature_stats()

        self.drift_report = self.combine_importance_stats(  # pylint: disable=attribute-defined-outside-init
            feature_importance=feature_importance,
            feature_stats=feature_stats,
        )

        if return_dataframe:
            return self.convert_report_to_dataframe()

        return self.drift_report

    def convert_report_to_dataframe(self):
        dataframe_dict = {}
        for feature, report in self.drift_report.items():
            dataframe_dict[feature] = report.dict()

        dataframe = pd.DataFrame.from_dict(dataframe_dict, orient="index")
        dataframe.reset_index(inplace=True)
        dataframe = dataframe.rename(columns={"index": "feature"})

        return dataframe

    def combine_importance_stats(
        self,
        feature_importance: Dict[Optional[str], FeatureImportance],
        feature_stats: Dict[str, DriftReport],
    ):
        for feature, stats in feature_stats.items():
            stats.feature_importance = feature_importance[feature].importance
            stats.feature_auc = feature_importance[feature].auc

        return feature_stats

    def create_feature_stats(self) -> Dict[str, DriftReport]:
        stats = {}
        for feature in self.features_and_target:
            stats[feature] = self.compute_feature_stats(feature=feature)
        return stats

    def compute_feature_stats(self, feature: str):
        feat_attr = self.extract_feature_attributes_for_stats(feature=feature)

        reference_stats = FeatureStats(
            data=feat_attr.reference_data,
            feature_type=feat_attr.feature_type,
            target_val=feat_attr.target_val,
        ).compute_stats()

        current_stats = FeatureStats(
            data=feat_attr.current_data,
            feature_type=feat_attr.feature_type,
            target_val=feat_attr.target_val,
        ).compute_stats()

        intersection = FeatureStats.compute_intersection(
            current_distribution=current_stats.historgram,
            reference_distribution=reference_stats.historgram,
        )
        return DriftReport(
            intersection=intersection,
            missing_records=reference_stats.missing_records,
            unique=reference_stats.unique,
            reference_distribution=reference_stats.historgram,
            current_distribution=current_stats.historgram,
            target_feature=feat_attr.target_val,
            feature_type=reference_stats.type_,
        )

    def get_ref_curr_feature_data(self, feature: str, data_ind: str = "X"):
        if data_ind == "X":
            ref_data = self.drift_data.reference_data.X[feature].to_numpy().reshape(-1, 1)
            curr_data = self.drift_data.current_data.X[feature].to_numpy().reshape(-1, 1)
        else:
            ref_data = self.drift_data.reference_data.y.reshape(-1, 1)
            curr_data = self.drift_data.current_data.y.reshape(-1, 1)

        return ref_data, curr_data

    def extract_feature_attributes_for_stats(self, feature: str) -> ExtractedAttributes:
        if feature == self.drift_features.target_feature:
            target_val = 1
            data_ind = "y"
        else:
            target_val = 0
            data_ind = "X"

        feature_type = self.drift_features.set_feature_type(feature=feature)
        ref_data, curr_data = self.get_ref_curr_feature_data(feature=feature, data_ind=data_ind)

        return ExtractedAttributes(
            reference_data=ref_data,
            current_data=curr_data,
            feature_type=feature_type,
            target_val=target_val,
        )

    def drift_report_available(self):
        if not hasattr(self, "drift_report"):
            return False
        return True

    def visualize_report(self, filename: str = "chart.html") -> alt.Chart:
        if not self.drift_report_available():
            self.run_drift_diagnostics()
        visualizer = DriftVisualizer(drift_report=self.drift_report)
        return visualizer.visualize_report(filename=filename)


class DriftReportParser:
    def __init__(
        self,
        drift_report: Dict[str, DriftReport],
    ):
        self.drift_report = drift_report
        self.feature_list = list(drift_report.keys())
        self.feature_distributions = ParsedFeatures()
        self.feature_importance = ParsedFeatureImportance()

    def report_to_dataframes(self) -> ParsedFeatureDataFrames:
        for feature in self.feature_list:
            self.parse_feature(feature=feature)

        dist_dataframe = pd.DataFrame.from_dict(self.feature_distributions.dict())
        importance_dataframe = pd.DataFrame.from_dict(self.feature_importance.dict())

        return ParsedFeatureDataFrames(
            distribution_dataframe=dist_dataframe,
            importance_dataframe=importance_dataframe,
        )

    def parse_feature(self, feature: str):
        feature_report: DriftReport = self.drift_report[feature]
        self.append_to_feature_data(feature=feature, feature_report=feature_report)
        self.append_to_feature_auc(feature=feature, feature_report=feature_report)

    def append_to_feature_auc(self, feature: str, feature_report: DriftReport):
        self.feature_importance.feature.append(feature)
        self.feature_importance.auc.append(feature_report.feature_auc)
        self.feature_importance.importance.append(feature_report.feature_importance)

    def append_to_feature_data(self, feature: str, feature_report: DriftReport):
        for label in ["reference", "current"]:
            hist: HistogramOutput = getattr(feature_report, f"{label}_distribution")
            self.feature_distributions.feature = [
                *self.feature_distributions.feature,
                *[feature] * hist.values.shape[0],
            ]
            self.feature_distributions.label = [*self.feature_distributions.label, *[label] * hist.values.shape[0]]
            self.feature_distributions.values = [*self.feature_distributions.values, *hist.values]
            self.feature_distributions.bins = [*self.feature_distributions.bins, *hist.bins]
            self.feature_distributions.feature_type = [
                *self.feature_distributions.feature_type,
                *[feature_report.feature_type] * hist.bins.shape[0],
            ]


class DriftVisualizer:
    def __init__(
        self,
        drift_report: Dict[str, DriftReport],
    ):
        self.report_parser = DriftReportParser(drift_report=drift_report)
        self.dataframes = self.report_parser.report_to_dataframes()

    def select_chart(
        self,
        chart_type: int,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None,
        dropdown_field_name: Optional[str] = None,
    ):
        chart_builder = next(
            chart_builder
            for chart_builder in AltairChart.__subclasses__()
            if chart_builder.validate_type(
                chart_type=chart_type,
            )
        )

        return chart_builder(
            data=data,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
            dropdown_field_name=dropdown_field_name,
        )

    def get_dataframe(self, chart_type: int):
        """Gets dataframe associated with chart type

        Args:
            chart_type (int): Chart type that is being built

        Returns:
            pandas dataframe
        """
        if ChartType(chart_type) == ChartType.AUC:
            return self.dataframes.importance_dataframe
        data = self.dataframes.distribution_dataframe
        return data.loc[data["feature_type"] == chart_type]

    def build_chart(
        self,
        chart_type: int,
        x_column: str,
        y_column: str,
        chart_title: str,
        color_column: Optional[str] = None,
        dropdown_field_name: Optional[str] = None,
    ):
        data = self.get_dataframe(chart_type=chart_type)

        chart_builder = self.select_chart(
            chart_type=chart_type,
            data=data,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
            dropdown_field_name=dropdown_field_name,
        )

        return chart_builder.build_chart(chart_title=chart_title)

    def get_chart_title(self, chart_type: int):
        if ChartType(chart_type) == ChartType.NUMERIC:
            return "Numeric Feature Distribution"
        return "Categorical Feature Distribution"

    def create_distribution_plots(self) -> List[alt.Chart]:
        charts = []
        chart_types = self.dataframes.distribution_dataframe["feature_type"].unique()
        for chart_type in chart_types:
            chart_title = self.get_chart_title(chart_type=chart_type)
            charts.append(
                self.build_chart(
                    chart_type=chart_type,
                    x_column="bins",
                    y_column="values",
                    color_column="label",
                    dropdown_field_name="feature",
                    chart_title=chart_title,
                )
            )
        return charts

    def create_auc_chart(self) -> List[alt.Chart]:
        chart_type = 2
        chart = [
            self.build_chart(
                chart_type=chart_type,
                x_column="auc",
                y_column="feature",
                chart_title="Feature AUC",
            )
        ]
        return chart

    def visualize_report(self, filename: str = "chart.html"):
        dist_charts = self.create_distribution_plots()
        auc_chart = self.create_auc_chart()

        final_chart = alt.vconcat(alt.hconcat(*dist_charts), *auc_chart)
        final_chart.save(
            filename,
            embed_options={"renderer": "svg"},
        )

        return final_chart
