# pylint: disable=redefined-outer-name,import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Any, List, Union

import pandas as pd
import polars as pl

DIR_PATH = os.path.dirname(__file__)
ProfileReport = Any


class DataProfiler:
    @staticmethod
    def create_profile_report(
        data: Union[pd.DataFrame, pl.DataFrame],
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
            name:
                Name of the report

        Returns:
            `ProfileReport`
        """
        from ydata_profiling import ProfileReport

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
        from ydata_profiling import ProfileReport

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
        from ydata_profiling import compare

        return compare(reports=reports)
