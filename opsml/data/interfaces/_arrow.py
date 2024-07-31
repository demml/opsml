from pathlib import Path
from typing import Dict, Optional

import pyarrow as pa
import pyarrow.parquet as pq

from opsml.data.formatter import generate_feature_schema
from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, Suffix


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

        load_path = path.with_suffix(self.data_suffix)
        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=load_path).read()

        self.data = pa_table

    @property
    def dependencies(self) -> Dict[str, str]:
        dependencies = {}

        try:
            dependencies["pyarrow"] = pa.__version__

        except AttributeError:
            pass

        return dependencies

    @property
    def data_type(self) -> str:
        return AllowedDataType.PYARROW.value

    @property
    def data_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.PARQUET.value

    @staticmethod
    def name() -> str:
        return ArrowData.__name__
