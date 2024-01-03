from pathlib import Path
from typing import Optional, cast

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from opsml.data.formatter import check_data_schema
from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, Feature, Suffix


class PandasData(DataInterface):
    """Pandas interface

    Args:
        data:
            Pandas DataFrame
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

    data: Optional[pd.DataFrame] = None

    def save_data(self, path: Path) -> None:
        """Saves pandas dataframe to parquet"""

        assert self.data is not None, "No data detected in interface"
        arrow_table = pa.Table.from_pandas(self.data, preserve_index=False)
        self.feature_map = {
            key: Feature(
                feature_type=str(value),
                shape=(1,),
            )
            for key, value in self.data.dtypes.to_dict().items()
        }
        pq.write_table(arrow_table, path)

    def load_data(self, path: Path) -> None:
        """Load parquet dataset to pandas dataframe"""

        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=path).read()

        data = check_data_schema(
            pa_table.to_pandas(),
            self.feature_map,
            self.data_type,
        )

        self.data = cast(pd.DataFrame, data)

    @property
    def data_type(self) -> str:
        return AllowedDataType.PANDAS.value

    @property
    def data_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.PARQUET.value

    @staticmethod
    def name() -> str:
        return PandasData.__name__
