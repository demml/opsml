from pathlib import Path
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from opsml.registry.data.interfaces.base import DataInterface
from opsml.registry.types import AllowedDataType, Feature, Suffix


class PandasData(DataInterface):
    data: Optional[pd.DataFrame] = None

    def save_data(self, path: Path) -> Path:
        """Saves pandas dataframe to parquet"""

        assert self.data is not None, "No data detected in interface"
        arrow_table = pa.Table.from_pandas(self.data, preserve_index=False)
        self.feature_map = {
            key: Feature(
                feature_type=str(value).lower(),
                shape=(1,),
            )
            for key, value in self.data.dtypes.to_dict().items()
        }
        save_path = path.with_suffix(Suffix.PARQUET.value)
        pq.write_table(arrow_table, path)

        return save_path

    def load_data(self, path: Path) -> None:
        """Load parquet dataset to pandas dataframe"""

        load_path = path.with_suffix(Suffix.PARQUET.value)
        pa_table: pa.Table = pq.ParquetDataset(path_or_paths=load_path).read()
        self.data = pa_table.to_pandas()

    @property
    def data_type(self) -> str:
        return AllowedDataType.PANDAS.value
