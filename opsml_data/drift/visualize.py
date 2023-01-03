import altair as alt
import pandas as pd
from typing import Optional
from opsml_data.drift.models import FeatureTypes


class AltairChart:
    def __init__(
        self,
        data: pd.DataFrame,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        color_column: Optional[str] = None,
        dropdown_field_name: Optional[str] = None,
    ):
        self.data = data
        self.x_column = x_column
        self.y_column = y_column
        self.color_column = color_column
        self.dropdown_field_name = dropdown_field_name

    def build_dropdown_selection(self, name: str):

        dropdown = alt.binding_select(
            options=self.data[self.dropdown_field_name].unique(),
            name=name,
        )
        dropdown_selection = alt.selection_single(
            fields=[self.dropdown_field_name],
            bind=dropdown,
        )

        return dropdown_selection

    def build_base_chart(
        self,
        dropdown_section: alt.Selection,
        chart_title: str,
    ) -> alt.Chart:
        chart = (
            alt.Chart(self.data)
            .encode(
                x=alt.X(self.x_column, title="Values"),
                y=alt.Y(self.y_column, title="Percentage"),
                color=alt.Color(
                    f"{self.color_column}:N",
                    title=self.color_column,
                    legend=alt.Legend(orient="right"),
                ),
                tooltip=[
                    alt.Tooltip(self.x_column, title="Bin"),
                    alt.Tooltip(self.y_column, title="Value"),
                ],
            )
            .add_selection(dropdown_section)
            .transform_filter(dropdown_section)
            .properties(width=300, title=chart_title)
        )

        return chart

    def build_chart(self):
        pass

    def validate_type(chart_type: str):
        pass


class CategoricalChart(AltairChart):
    def build_chart(self, chart_title: str) -> alt.Chart:
        dropdown = self.build_dropdown_selection(name="Categorical")
        chart = self.build_base_chart(
            dropdown_section=dropdown,
            chart_title=chart_title,
        )
        chart = chart.mark_bar()
        return chart

    @staticmethod
    def validate_type(chart_type: str):
        if chart_type.lower() == "categorical":
            return True
        return False


class NumericChart(AltairChart):
    def build_chart(self, chart_title: str) -> alt.Chart:
        dropdown = self.build_dropdown_selection(name="Numeric")
        chart: alt.Chart = self.build_base_chart(
            dropdown_section=dropdown,
            chart_title=chart_title,
        )
        chart = chart.mark_area()
        return chart

    @staticmethod
    def validate_type(chart_type: str):
        if chart_type.lower() == "numeric":
            return True
        return False


class AucChart(AltairChart):
    def build_chart(self, chart_title: str) -> alt.Chart:
        feature_auc_chart = (
            alt.Chart(self.data)
            .mark_bar()
            .encode(
                y=alt.X(self.x_column, title="Values"),
                x=alt.Y(
                    self.y_column,
                    title=self.y_column,
                    sort="-x",
                    axis=alt.Axis(
                        domain=True,
                        offset=1,
                        labelAngle=-45,
                    ),
                ),
                color=alt.condition(
                    f"datum.{self.x_column}>=.6",
                    alt.ColorValue("red"),
                    alt.ColorValue("#BEBFC1"),
                ),
            )
            .properties(title=chart_title)
        )

        return feature_auc_chart

    @staticmethod
    def validate_type(plot_type: str):
        if plot_type.lower() == "auc":
            return True
        return False

    # else:

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
