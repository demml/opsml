import warnings
from typing import Optional

import altair as alt

from opsml_artifacts.drift.types import ChartType

warnings.simplefilter(action="ignore", category=FutureWarning)  # type: ignore
import pandas as pd  # noqa: E402 #pylint: disable=[wrong-import-position,wrong-import-order]


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

    def build_chart(self, chart_title: str):
        raise NotImplementedError

    @staticmethod
    def validate_type(chart_type: int):
        raise NotImplementedError


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
    def validate_type(chart_type: int):
        return ChartType(chart_type) == ChartType.CATEGORICAL


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
    def validate_type(chart_type: int):
        return ChartType(chart_type) == ChartType.NUMERIC


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
    def validate_type(chart_type: int):
        return ChartType(chart_type) == ChartType.AUC
