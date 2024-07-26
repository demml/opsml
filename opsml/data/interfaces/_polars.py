from pathlib import Path
from typing import Optional

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from opsml.data.formatter import check_data_schema, generate_feature_schema
from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, Suffix


class PolarsData(DataInterface):
    """Polars data interface

    Args:
        data:
            Polars DataFrame
        dependent_vars:
            List of dependent variables. Can be string or index if using numpy
        data_splits:
            Optional list of `DataSplit`
        data_profile:
            Optional ydata-profiling `ProfileReport`
        feature_map:
            Dictionary of features -> automatically generated
        feature_descriptions:
            Dictionary or feature descriptions
        sql_logic:
            Sql logic used to generate data
    """

    data: Optional[pl.DataFrame] = None

    def save_data(self, path: Path) -> None:
        """Saves pandas dataframe to parquet"""

        assert self.data is not None, "No data detected in interface"

        self.feature_map = generate_feature_schema(
            self.data,
            self.data_type,
        )

        pq.write_table(self.data.to_arrow(), path)

    def load_data(self, path: Path) -> None:
        """Load parquet dataset to pandas dataframe"""

        load_path = path.with_suffix(self.data_suffix)
        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=load_path).read()

        # attempt to validate schema
        data = check_data_schema(
            pl.from_arrow(data=pa_table),
            self.feature_map,
            self.data_type,
        )
        assert isinstance(data, pl.DataFrame), "Data is not a Polars DataFrame"

        self.data = data

    @property
    def data_type(self) -> str:
        return AllowedDataType.POLARS.value

    @property
    def data_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.PARQUET.value

    @staticmethod
    def name() -> str:
        return PolarsData.__name__
