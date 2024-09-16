# pylint: disable=redefined-outer-name,import-outside-toplevel
# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Union

import pandas as pd
import polars as pl
from scouter import DataProfile, Profiler


class DataProfiler:
    @staticmethod
    def create_profile_report(
        data: Union[pd.DataFrame, pl.DataFrame],
        bin_size: int = 20,
    ) -> DataProfile:
        """
        Creates a `scouter` data profile report

        Args:
            data:
                data to profile
            bin_size:
                number of bins for histograms. Default is 20

        Returns:
            `DataProfile`
        """
        profiler = Profiler()

        return profiler.create_data_profile(data=data, bin_size=bin_size)

    @staticmethod
    def load_profile(data: str) -> DataProfile:
        """Loads a `ProfileReport` from data bytes

        Args:
            data:
                `DataProfile` as json string

        Returns:
            `DataProfile`
        """

        return DataProfile.model_validate_json(data)
