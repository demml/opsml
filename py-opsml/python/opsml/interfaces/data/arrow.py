from pathlib import Path
from typing import Optional

import pyarrow as pa  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from opsml.interfaces.data.features.formatter import generate_feature_schema
from opsml.interfaces.data.base import DataInterface
from opsml import DataType, Suffix


class ArrowData(DataInterface):
    """Arrow Table data interface

    Args:
        data:
            Pyarrow Table
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

    data: Optional[pa.Table] = None

    def save_data(self, path: Path) -> None:
        """Saves pandas dataframe to parquet"""

        assert self.data is not None, "No data detected in interface"
        self.feature_map = generate_feature_schema(self.data, self.data_type)
        pq.write_table(self.data, path)

    def load_data(self, path: Path) -> None:
        """Load parquet dataset to pandas dataframe"""

        load_path = path.with_suffix(Suffix.Parquet.as_string())
        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=load_path).read()

        self.data = pa_table

    @property
    def data_type(self) -> DataType:
        return DataType.Pyarrow

    @staticmethod
    def name() -> str:
        return ArrowData.__name__
