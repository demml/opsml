from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
import altair as alt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, roc_curve
from opsml_data.drift.drift_utils import shipt_theme
from opsml_data.drift.models import (
    DriftData,
    HistogramOutput,
    FeatureStatsOutput,
    FeatureImportance,
    DriftReport,
    ExtractedAttributes,
)

alt.themes.register("shipt", shipt_theme)
alt.themes.enable("shipt")


class FeatureTypes(Enum):
    CATEGORICAL = 0
    NUMERIC = 1


class FeatureImportanceCalculator:
    """Provides metrics for drift detections"""

    def __init__(
        self,
        features: List[str],
        data: DriftData,
        target_feature: str,
    ):
        self.log_reg = LogisticRegression()
        self.features = features
        self.data = data
        self.features_and_target = [*self.features, *[target_feature]]

    def compute_auc(self, X: np.ndarray, y: np.ndarray) -> float:
        self.log_reg.fit(X, y)
        preds = self.log_reg.predict_proba(X)[::, 1]
        fpr, tpr, _ = roc_curve(y, preds, pos_label=1)
        return auc(fpr, tpr)

    def calculate_feature_importance(self):
        self.log_reg.fit(self.data.X, self.data.y)
        coefs = list(self.log_reg.coef_[0])
        coefs.append(None)  # for target

        return coefs

    def calculate_feature_auc(self):
        feature_aucs = []
        X = np.hstack((self.data.X[self.features].to_numpy(), self.data.target))
        for feature in range(X.shape[1]):
            computed_auc = self.compute_auc(X=X[:, feature].reshape(-1, 1), y=self.data.y)
            feature_aucs.append(computed_auc)

        return feature_aucs

    def combine_feature_importance_auc(
        self, feature_importances: List[float], feature_aucs: List[float]
    ) -> Dict[str, FeatureImportance]:

        feature_dict = {}
        for feature_name, importance, computed_auc in zip(self.features_and_target, feature_importances, feature_aucs):
            feature_dict[feature_name] = FeatureImportance(importance=importance, auc=computed_auc)

        return feature_dict

    def compute_importance(
        self,
    ) -> Dict[str, FeatureImportance]:
        """Computes feature importance from object attributes

        Returns
            Dictionary containing features and their importances
        """

        feature_importances = self.calculate_feature_importance()
        feature_aucs = self.calculate_feature_auc()
        combined_features = self.combine_feature_importance_auc(
            feature_importances=feature_importances, feature_aucs=feature_aucs
        )
        return combined_features


class DriftFeatures:
    """Computes relevant feature attributes used in drift detection"""

    def __init__(
        self,
        dtypes: Dict[str, Any],
        categorical_features: Optional[List[str]] = None,
        target_feature: Optional[str] = None,
    ):

        self.dtypes = dtypes
        self.target_feature = target_feature
        self.feature_list = self.create_feature_list()
        self.categorical_features = self.get_categorical_features(categorical_features=categorical_features)

    def create_feature_list(self) -> List[str]:
        feature_mapping = self.get_feature_types()
        return list(feature_mapping.keys())

    def get_categorical_features(self, categorical_features: Optional[List[str]] = None) -> List[str]:

        if not bool(categorical_features):
            categorical_features = []

        return [feature for feature in self.feature_list if feature in categorical_features]

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

        X_drift = self.create_x_data()
        y_drift = self.create_y_data()
        target = np.vstack((self.reference_data.y.reshape(-1, 1), self.current_data.y.reshape(-1, 1)))

        return DriftData(X=X_drift, y=y_drift, target=target)


class FeatureHistogram:
    def __init__(
        self,
        bins: Union[int, List[Union[int, float]]],
        feature_type: int,
    ):
        self.bins = bins
        self.feature_type = feature_type

    def compute_histogram(self, data: np.ndarray) -> Tuple[List[float], List[float]]:
        hist, edges = np.histogram(data, bins=self.bins, density=False)
        hist = np.divide(hist, data.shape[0])

        return edges, hist

    def compute_feature_histogram(self, data: np.ndarray) -> HistogramOutput:
        if FeatureTypes(self.feature_type) == FeatureTypes.NUMERIC:
            edges, hist = self.compute_histogram(data=data)
        else:
            edges, hist = np.unique(data, return_counts=True)

        return HistogramOutput(histogram=hist, edges=edges)


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
    def compute_intersection(current_hist, reference_hist):
        intersection = np.sum(current_hist) / np.sum(reference_hist)
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
        y_reference: np.array,
        x_current: pd.DataFrame,
        y_current: np.array,
        target_feature_name: str,
        categorical_features: Optional[List[str]] = None,
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

        self.drift_features = DriftFeatures(
            dtypes=dict(x_reference.dtypes),
            categorical_features=categorical_features,
            target_feature=target_feature_name,
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
        self.features_and_target = [*self.drift_features.feature_list, *[target_feature_name]]

    def run_drift_diagnostics(self, return_dataframe: bool = False):
        """Computes drift diagnostics between reference and current
        data based upon column mapping

        Returns:
            return_df (pd.DataFrame): Dataframe of computed drift statistics.
        """

        feature_importance = self.importance_calc.compute_importance()
        feature_stats = self.create_feature_stats()

        self.drift_report = self.combine_importance_auc(
            feature_importance=feature_importance,
            feature_stats=feature_stats,
        )

        if return_dataframe:
            return self.convert_report_to_dataframe()

    def convert_report_to_dataframe(self):
        dataframe_dict = {}
        for feature, report in self.drift_report.items():
            dataframe_dict[feature] = report.dict()

        dataframe = pd.DataFrame.from_dict(dataframe_dict, orient="index")
        dataframe.reset_index(inplace=True)
        dataframe = dataframe.rename(columns={"index": "feature"})

        return dataframe

    def combine_importance_auc(
        self,
        feature_importance: Dict[str, FeatureImportance],
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

        # using bins from reference stats
        current_stats = FeatureStats(
            data=feat_attr.current_data,
            feature_type=feat_attr.feature_type,
            target_val=feat_attr.target_val,
            bins=reference_stats.historgram.edges,
        ).compute_stats()

        intersection = FeatureStats.compute_intersection(
            current_hist=current_stats.historgram.histogram,
            reference_hist=reference_stats.historgram.histogram,
        )
        return DriftReport(
            intersection=intersection,
            missing_records=reference_stats.missing_records,
            unique=reference_stats.unique,
            reference_distribution=reference_stats.historgram,
            current_distribution=current_stats.historgram,
            target_feature=feat_attr.target_val,
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

    def convert_diagnostics_to_dataframe(
        self,
        feature_importance: Dict[str, Dict[str, Union[float, int]]],
        feature_stats: Dict[str, Dict[str, Union[str, int, float]]],
    ) -> pd.DataFrame:
        combined_data = {}
        for feature in self.features_and_target:
            combined_data[feature] = {}
            combined_data[feature].update(feature_importance[feature])
            combined_data[feature].update(feature_stats[feature])

        return pd.DataFrame.from_dict(combined_data, orient="index")

    @classmethod
    def _parse_drift_df(
        cls,
        dataframe: pd.DataFrame,
        reference_label: str,
        current_label: str,
    ):
        num_list = []
        cat_list = []
        data_dict = {
            "num_data": None,
            "cat_data": None,
        }
        for feature in dataframe["feature"].unique():
            subset = dataframe.loc[dataframe["feature"] == feature]
            reference = pd.DataFrame.from_dict(subset["reference_distribution"].values[0])
            reference["data"] = reference_label
            current = pd.DataFrame.from_dict(
                subset["current_distribution"].values[0],
            )
            current["data"] = current_label
            plot_data = pd.concat([reference, current], axis=0)
            plot_data["feature"] = feature
            if subset["type"].values[0] == "categorical":
                cat_list.append(plot_data)
            else:
                num_list.append(plot_data)

        if len(num_list) > 0:
            data_dict["num_data"] = pd.concat(
                num_list,
                axis=0,
            )

        if len(cat_list) > 0:
            data_dict["cat_data"] = pd.concat(
                cat_list,
                axis=0,
            )

        return data_dict

    @classmethod
    def _build_cat_plot(cls, cat_data: pd.DataFrame = None):

        if cat_data is None:
            return None

        cat_dropdown = alt.binding_select(
            options=cat_data["feature"].unique(),
            name="Categorical Feature ",
        )
        cat_selection = alt.selection_single(
            fields=["feature"],
            bind=cat_dropdown,
        )

        cat_chart = (
            alt.Chart(cat_data)
            .mark_bar()
            .encode(
                x=alt.X("edges", title="Values"),
                y=alt.Y("hist", title="Count"),
                color=alt.Color(
                    "data:N",
                    title="Data",
                    legend=alt.Legend(orient="right"),
                ),
                tooltip="hist:N",
            )
            .add_selection(cat_selection)
            .transform_filter(cat_selection)
            .properties(width=300, title="Categorical")
        )

        return cat_chart

    @classmethod
    def _build_num_plot(cls, num_data: pd.DataFrame = None):

        if num_data is None:
            return None
        num_dropdown = alt.binding_select(
            options=num_data["feature"].unique(),
            name="Numeric Feature ",
        )
        num_selection = alt.selection_single(
            fields=["feature"],
            bind=num_dropdown,
        )

        num_chart = (
            alt.Chart(num_data)
            .encode(
                x=alt.X("edges", title="Values"),
                y=alt.Y("hist", title="Count"),
                color=alt.Color(
                    "data:N",
                    title="Data",
                    legend=alt.Legend(orient="right"),
                ),
                tooltip="hist:N",
            )
            .add_selection(num_selection)
            .mark_area()
            .transform_filter(num_selection)
            .properties(width=300, title="Numeric")
        )

        return num_chart

    @classmethod
    def _feature_auc_plot(cls, dataframe: pd.DataFrame = None):

        if not bool(dataframe):
            return None
        # feature auc
        feature_auc_chart = (
            alt.Chart(dataframe)
            .mark_bar()
            .encode(
                y=alt.X("feature_auc", title="Values"),
                x=alt.Y(
                    "feature",
                    title="Feature",
                    sort="-x",
                    axis=alt.Axis(
                        domain=True,
                        offset=1,
                        labelAngle=-45,
                    ),
                ),
                color=alt.condition(
                    "datum.feature_auc>=.6",
                    alt.ColorValue("red"),
                    alt.ColorValue("#BEBFC1"),
                ),
            )
            .properties(title="Feature Importance")
        )

        return feature_auc_chart

    @classmethod
    def _generate_final_chart(
        cls,
        num_chart=None,
        cat_chart=None,
        feature_auc_chart=None,
    ):

        if num_chart is not None and cat_chart is not None:
            chart1 = alt.hconcat(
                num_chart,
                cat_chart,
            )

            chart = alt.vconcat(
                chart1,
                feature_auc_chart,
            )

        if num_chart is not None and cat_chart is None:
            chart = alt.hconcat(
                feature_auc_chart,
                num_chart,
            )

        if cat_chart is not None and num_chart is None:
            chart = alt.hconcat(
                feature_auc_chart,
                cat_chart,
            )

        if num_chart is None and cat_chart is None:
            chart = feature_auc_chart

        return chart

    @classmethod
    def chart_drift_diagnostics(
        cls,
        dataframe: pd.DataFrame,
        reference_label: str = "reference",
        current_label: str = "current",
        save_fig: bool = True,
        filename: str = "chart.html",
    ):
        """Visualize drift diagnostics from a pandas dataframe
        that was generated by "run_drift_diagnostics".

        Args:
            dataframe: Pandas dataframe from "run_drift_diagnostics
            reference_label: Label that was used for reference data when
            computing metrics.
            current_label: Label that was used for current data when
            computing metrics.
            save_fig: Whether to save the chart or not.
            filename: Filename to save chart to.
        Returns:
            chart (Alatair Chart): Chart created from drift dataframe.
        """

        data_dict = cls._parse_drift_df(
            dataframe=dataframe,
            reference_label=reference_label,
            current_label=current_label,
        )
        cat_chart = cls._build_cat_plot(
            data_dict["cat_data"],
        )

        num_chart = cls._build_num_plot(
            data_dict["num_data"],
        )

        feature_auc_chart = cls._feature_auc_plot(dataframe)
        chart = cls._generate_final_chart(
            num_chart=num_chart,
            cat_chart=cat_chart,
            feature_auc_chart=feature_auc_chart,
        )

        if save_fig:
            chart.save(
                filename,
                embed_options={"renderer": "svg"},
            )
        return chart
