# pylint: disable=redefined-outer-name,import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Union, Optional

import pandas as pd
import polars as pl
from scouter import Profiler, DataProfile


class DataProfiler:
    @staticmethod
    def create_profile_report(
        data: Union[pd.DataFrame, pl.DataFrame],
        bin_size: int = 20,
        features: Optional[List[str]] = None,
    ) -> DataProfile:
        """
        Creates a `scouter` data profile report

        Args:
            data:
                data to profile
            bin_size:
                number of bins for histograms. Default is 20
            features:
                Optional list of features to profile

        Returns:
            `DataProfile`
        """
        profiler = Profiler()

        return profiler.create_data_profile(data=data, features=features, bin_size=bin_size)

    @staticmethod
    def load_profile(data: str) -> DataProfile:
        """Loads a `ProfileReport` from data bytes

        Args:
            data:
                `DataProfile` as json string

        Returns:
            `DataProfile`
        """

        return DataProfile.load_from_json(data)
