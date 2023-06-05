import os
from typing import List, Union

import pandas as pd
import polars as pl
from ydata_profiling import ProfileReport, compare

DIR_PATH = os.path.dirname(__file__)


class DataProfiler:
    @staticmethod
    def create_profile_report(
        data: Union[pl.DataFrame, pd.DataFrame],
        name: str,
        sample_perc: float = 1,
    ) -> ProfileReport:
        """
        Creates a `ydata-profiling` report

        Args:
            data:
                Pandas dataframe
            sample_perc:
                Percentage to use for sampling

        Returns:
            `ProfileReport`
        """
        kwargs = {"title": f"Profile report for {name}"}

        if isinstance(data, pl.DataFrame):
            if sample_perc < 1:
                return ProfileReport(
                    df=data.sample(fraction=sample_perc, with_replacement=False, shuffle=True).to_pandas(),
                    config_file=os.path.join(DIR_PATH, "profile_config.yml"),
                    lazy=False,
                    **kwargs,
                )

            return ProfileReport(
                df=data.to_pandas(),
                config_file=os.path.join(DIR_PATH, "profile_config.yml"),
                lazy=False,
                **kwargs,
            )

        if sample_perc < 1:
            return ProfileReport(
                df=data.sample(frac=sample_perc, replace=False),
                config_file=os.path.join(DIR_PATH, "profile_config.yml"),
                lazy=False,
                **kwargs,
            )

        return ProfileReport(
            df=data,
            config_file=os.path.join(DIR_PATH, "profile_config.yml"),
            lazy=False,
            **kwargs,
        )

    @staticmethod
    def load_profile(data: bytes) -> ProfileReport:
        """Loads a `ProfileReport` from data bytes

        Args:
            data:
                `ProfileReport` in bytes

        Returns:
            `ProfileReport`
        """
        profile = ProfileReport()
        profile.loads(data)
        return profile

    @staticmethod
    def compare_reports(reports: List[ProfileReport]) -> ProfileReport:
        """Compares ProfileReports

        Args:
            reports:
                List of `ProfileReport`

        Returns:
            `ProfileReport`
        """
        return compare(reports=reports)
