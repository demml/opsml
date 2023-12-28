from pathlib import Path
from typing import Optional, cast

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from opsml.registry.data.formatter import check_data_schema
from opsml.registry.data.interfaces.base import DataInterface
from opsml.registry.types import AllowedDataType, Feature, Suffix


class PandasData(DataInterface):
    """Pandas interface

    Args:
        data:
            Pandas DataFrame
        dependent_vars:
            List of dependent variables. Can be string or index if using numpy
        data_splits:
            Optional list of `DataSplit`
        sql_logic:
            Dictionary of strings containing sql logic or sql files used to create the data
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

    def save_data(self, path: Path) -> Path:
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
        save_path = path.with_suffix(self.storage_suffix)
        pq.write_table(arrow_table, path)

        return save_path

    def load_data(self, path: Path) -> None:
        """Load parquet dataset to pandas dataframe"""

        load_path = path.with_suffix(self.storage_suffix)
        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=load_path).read()

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
    def storage_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.PARQUET.value
