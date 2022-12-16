from typing import Any, Dict, Iterable, List

import altair as alt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, roc_curve

from ..helpers import exceptions
from .drift_utils import shipt_theme

alt.themes.register("shipt", shipt_theme)
alt.themes.enable("shipt")

# this needs to be refactored into bette code at some point (steven)
class Drifter:
    bins = 20

    @classmethod
    def _compute_intersection(
        cls,
        cur_hist,
        ref_hist,
    ):
        intersection = np.sum(cur_hist) / np.sum(ref_hist)

        return intersection

    @classmethod
    def _get_feature_types(
        cls,
        feature_mapping: Dict[str, str],
    ):
        if not isinstance(feature_mapping, dict):
            raise exceptions.NotofTypeDictionary(
                """Expected dictionary type for
                feature mappings"""
            )

        for key, val in feature_mapping.items():
            if val == "O":
                feature_mapping[key] = "str"
            else:
                feature_mapping[key] = str(val)
        return feature_mapping

    @classmethod
    def _count_missing(cls, data: Iterable):
        if not isinstance(data, np.ndarray):
            raise exceptions.NotofTypeArray(
                """Data is expected to be of
            type np.array"""
            )
        return len(np.argwhere(np.isnan(data)))

    @classmethod
    def _compute_feature_stats(
        cls,
        reference_data: Iterable,
        current_data: Iterable,
        reference_label: str,
        current_label: str,
        feature_type: str,
    ) -> Dict[str, Any]:

        """Computes the drift of a feature given reference
        and current datasets. Currently works with dataframes

        Args:
            reference_data: Reference data
            current_data: Current data
            reference_label: Reference data label
            current_label: Current data label
            feature_type: Whether feature is "categorical" or
            "numerical".

        Returns:
            Dictionary

        """
        if not isinstance(reference_data, np.ndarray):
            reference_data = np.array(reference_data)

        if not isinstance(current_data, np.ndarray):
            current_data = np.array(current_data)

        # count number of missing records
        nbr_missing_records = cls._count_missing(reference_data)
        percent_missing = round((nbr_missing_records / reference_data.shape[0]) * 100, 2)  # noqa

        # Remove missing values
        reference_data = reference_data[~np.isnan(reference_data)]
        current_data = current_data[~np.isnan(current_data)]

        if feature_type == "numerical":
            ref_hist, ref_edge = np.histogram(
                reference_data,
                bins=cls.bins,
                density=False,
            )
            cur_hist, cur_edge = np.histogram(
                current_data,
                bins=ref_edge,
                density=False,
            )

            ref_hist = ref_hist / reference_data.shape[0]
            cur_hist = cur_hist / current_data.shape[0]

            intersection = cls._compute_intersection(
                cur_hist,
                ref_hist,
            )

        else:
            ref_edge, ref_hist = np.unique(
                reference_data,
                return_counts=True,
            )
            cur_edge, cur_hist = np.unique(
                current_data,
                return_counts=True,
            )
            intersection = cls._compute_intersection(cur_hist, ref_hist)

        unique_values = len(np.unique(reference_data))
        results = {
            f"{reference_label}_histogram": {
                "hist": ref_hist.astype(np.float32).tolist(),
                "edges": ref_edge[1:].astype(np.float32).tolist(),
            },
            f"{current_label}_histogram": {
                "hist": cur_hist.astype(np.float32).tolist(),
                "edges": ref_edge[1:].astype(np.float32).tolist(),  # noqa
            },
            "intersection": intersection,
            "missing_records": f"{nbr_missing_records}, {percent_missing}%",  # noqa
            "unique": unique_values,
        }

        return results

    @classmethod
    def _compute_log_reg_auc(
        cls,
        x_train,
        y_train,
    ):

        # Create model
        log_reg = LogisticRegression()
        log_reg.fit(x_train, y_train)

        preds = log_reg.predict_proba(x_train)[::, 1]
        fpr, tpr, thresholds = roc_curve(
            y_train,
            preds,
            pos_label=1,
        )
        auc_score = auc(fpr, tpr)

        return auc_score

    @classmethod
    def _compute_drift_feature_importance(
        cls,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        feature_list: List[str],
        target_feature: str = None,
    ):
        # if not type(reference_data) == pd.DataFrame:
        # raise exceptions.NotDataFrame(
        # """Reference and current data must be of type pd.DataFrame"""
        # )
        # target type can be reg, binary, multiclass

        if not type(reference_data) == pd.DataFrame or not type(current_data) == pd.DataFrame:
            raise exceptions.NotDataFrame(
                """Reference and current data must be of type
                pd.DataFrame"""
            )

        feature_importance_dict = {}

        # Run feature importance
        ref_targets = np.zeros((reference_data.shape[0],))
        current_targets = np.ones((current_data.shape[0],))
        # reference_data["target"] = 0
        # current_data["target"] = 1

        df = pd.concat([reference_data, current_data])
        df.dropna(inplace=True)

        # Set X data
        x_train = df[feature_list]

        # y_train is the indicator between reference and current data
        y_train = np.hstack((ref_targets, current_targets))

        # Remove missing indices

        # Fit model and return importances
        log_reg = LogisticRegression()
        log_reg.fit(x_train, y_train)
        preds = log_reg.predict_proba(x_train)[::, 1]
        importances = log_reg.coef_[0]

        if not len(importances) == len(feature_list):
            raise exceptions.LengthMismatch(
                """Number of features and feature
                importances are not the same"""
            )

        for feature, importance in zip(feature_list, importances):

            auc = cls._compute_log_reg_auc(
                x_train[feature].to_numpy().reshape(-1, 1),
                y_train,
            )
            feature_importance_dict[feature] = {
                "feature_importance": importance,
                "feature_auc": auc,
            }

        if target_feature is not None:

            auc = cls._compute_log_reg_auc(
                df[target_feature].to_numpy().reshape(-1, 1),
                y_train,
            )

            feature_importance_dict[target_feature] = {
                "feature_importance": None,
                "feature_auc": auc,
            }

        return feature_importance_dict

    @classmethod
    def run_drift_diagnostics(
        cls,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        feature_mapping: Dict[str, str] = None,
        categorical_features: List[str] = [],
        target_feature: str = None,
        exclude_cols: List[str] = None,
        current_label: str = "current",
        reference_label: str = "reference",
        return_df: bool = False,
    ):

        """Computes drift diagnostics between reference and current
        data based upon column mapping

        Args:
            reference_data: Pandas dataframe of reference data
            current_data: Pandas dataframe containing current data
            feature_mapping: Dictionary containing features (keys) and
            their types
            target_feature: Name of target variable
            exclude_cols: List of columns to exclude
            current_label: Label for current data
            reference_label: Label for reference data
            return_df: Whether to return pandas dataframe or not

        Returns:
            return_df (pd.DataFrame): Dataframe of computed drift statistics.
        """

        # Compute feature drift
        feature_dict = {}

        if feature_mapping is None:
            feature_mapping = cls._get_feature_types(
                feature_mapping=dict(
                    reference_data.dtypes,
                )
            )

        if exclude_cols is None:
            exclude_cols = []

        feature_list = list(set(feature_mapping.keys()) - set(exclude_cols))
        cat_features = [feature for feature in feature_list if feature in categorical_features]  # noqa

        # Create global model and compute feature importance
        feature_importance = cls._compute_drift_feature_importance(
            reference_data,
            current_data,
            feature_list=feature_list,
            target_feature=target_feature,
        )

        if target_feature is not None:
            if not isinstance(target_feature, list):
                target_feature = [target_feature]
        else:
            target_feature = []

        for feature in [*feature_list, *target_feature]:
            if feature in cat_features:
                feature_type = "categorical"
            else:
                feature_type = "numerical"

            feature_dict[feature] = dict.fromkeys(
                [
                    "type",
                    "intersection",
                    "missing_records",
                    "unique",
                    "reference_distribution",
                    "current_distribution",
                    "feature_importance",
                    "feature_auc",
                    "reference_label",
                    "current_label",
                    "target_feature",
                ]
            )

            feature_dict[feature]["type"] = feature_type

            # Subset data
            ref_data = reference_data[feature]
            cur_data = current_data[feature]

            # Create distributions and intersection between current and reference data # noqa
            results = cls._compute_feature_stats(
                reference_data=ref_data,
                current_data=cur_data,
                reference_label=reference_label,
                current_label=current_label,
                feature_type=feature_type,
            )

            feature_dict[feature]["intersection"] = results["intersection"]  # noqa
            feature_dict[feature]["missing_records"] = results["missing_records"]  # noqa
            feature_dict[feature]["unique"] = results["unique"]

            feature_dict[feature]["feature_importance"] = feature_importance[feature]["feature_importance"]  # noqa
            feature_dict[feature]["feature_auc"] = feature_importance[feature]["feature_auc"]  # noqa

            feature_dict[feature]["reference_distribution"] = results[f"{reference_label}_histogram"]
            feature_dict[feature]["current_distribution"] = results[f"{current_label}_histogram"]

            feature_dict[feature]["reference_label"] = reference_label
            feature_dict[feature]["current_label"] = current_label

            if feature in target_feature:
                feature_dict[feature]["target_feature"] = 1

            else:
                feature_dict[feature]["target_feature"] = 0

        if return_df:
            df = pd.DataFrame.from_dict(feature_dict, orient="index").reset_index().rename(columns={"index": "feature"})
            return df

    @classmethod
    def _parse_drift_df(
        cls,
        df: pd.DataFrame,
        reference_label: str,
        current_label: str,
    ):
        num_list = []
        cat_list = []
        data_dict = {
            "num_data": None,
            "cat_data": None,
        }
        for feature in df["feature"].unique():
            subset = df.loc[df["feature"] == feature]
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
            name="Numerical Feature ",
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
            .properties(width=300, title="Numerical")
        )

        return num_chart

    @classmethod
    def _feature_auc_plot(cls, df: pd.DataFrame = None):

        if df is None:
            return None
        # feature auc
        feature_auc_chart = (
            alt.Chart(df)
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
        df: pd.DataFrame,
        reference_label: str = "reference",
        current_label: str = "current",
        save_fig: bool = True,
        filename: str = "chart.html",
    ):
        """Visualize drift diagnostics from a pandas dataframe
        that was generated by "run_drift_diagnostics".

        Args:
            df: Pandas dataframe from "run_drift_diagnostics
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
            df=df,
            reference_label=reference_label,
            current_label=current_label,
        )
        cat_chart = cls._build_cat_plot(
            data_dict["cat_data"],
        )

        num_chart = cls._build_num_plot(
            data_dict["num_data"],
        )

        feature_auc_chart = cls._feature_auc_plot(df)
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
