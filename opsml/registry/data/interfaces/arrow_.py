from pathlib import Path
from typing import Optional

import pyarrow as pa
import pyarrow.parquet as pq

from opsml.registry.data.interfaces.base import DataInterface
from opsml.registry.types import AllowedDataType, Feature, Suffix


class PolarsData(DataInterface):
    data: Optional[pa.Table] = None

    def save_data(self, path: Path) -> Path:
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
        save_path = path.with_suffix(Suffix.PARQUET.value)
        pq.write_table(self.data, path)

        return save_path

    def load_data(self, path: Path) -> None:
        """Load parquet dataset to pandas dataframe"""

        load_path = path.with_suffix(Suffix.PARQUET.value)
        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=load_path).read()

        self.data = pa_table

    @property
    def data_type(self) -> str:
        return AllowedDataType.PYARROW.value
