from pathlib import Path
from typing import Optional

import pyarrow as pa
import pyarrow.parquet as pq

from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, Feature, Suffix


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
        schema = self.data.schema
        self.feature_map = {
            feature: Feature(
                feature_type=str(type_),
                shape=(1,),
            )
            for feature, type_ in zip(schema.names, schema.types)
        }

        pq.write_table(self.data, path)

    def load_data(self, path: Path) -> None:
        """Load parquet dataset to pandas dataframe"""

        load_path = path.with_suffix(self.data_suffix)
        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=load_path).read()

        self.data = pa_table

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
