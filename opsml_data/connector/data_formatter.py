import pandas as pd
import numpy as np
import pyarrow as pa
from typing import Union
from opsml_data.helpers.exceptions import NotOfCorrectType
from typing import Dict


class DataFormatter:
    @staticmethod
    def convert_data_to_arrow(data: Union[pd.DataFrame, np.array]):
        if isinstance(data, pd.DataFrame):
            return pa.Table.from_pandas(
                data,
                preserve_index=False,
            )

        elif isinstance(data, np.ndarray):
            return pa.array(data)

        elif isinstance(data, pa.Table):
            return data

        else:
            raise NotOfCorrectType(
                """Data type was not of Numpy array, pandas dataframe or pyarrow table"""  # noqa
            )

    @staticmethod
    def get_schema(data: pa.Table) -> Dict[str, str]:
        schema = data.schema
        feature_map = {}

        for feature, type_ in zip(schema.names, schema.types):
            feature_map[feature] = str(type_)

        return feature_map
