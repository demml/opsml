from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from opsml_artifacts.registry.model.types import DataDtypes, Feature, ModelData


def get_dtype_shape(data: Any):

    return str(data.dtype), data.shape[1:]


def get_feature_info(type_: str, shape: List[Optional[int]]) -> Feature:
    if "int" in type_:
        return Feature(feature_type="INT", shape=shape)
    if "float" in type_:
        return Feature(feature_type="FLOAT", shape=shape)
    return Feature(feature_type="STR", shape=shape)


class FloatTypeConverter:
    def __init__(self, convert_all: bool):
        """Helper for converting float type or all columns to Float32

        Args:
            all (bool): Boolean indicating whether to convert all columns or not
        """
        self.convert_all = convert_all

    def _convert_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        for feature, feature_type in zip(data.columns, data.dtypes):

            if not self.convert_all:
                if DataDtypes.FLOAT64 in str(feature_type):
                    data[feature] = data[feature].astype(np.float32)
            else:
                data[feature] = data[feature].astype(np.float32)
        return data

    def _convert_array(self, data: NDArray) -> NDArray:
        dtype = str(data.dtype)
        if dtype != DataDtypes.STRING:
            return data.astype(np.float32, copy=False)
        return data

    def _convert_dict(self, data: Dict[str, NDArray]) -> Dict[str, NDArray]:
        for key, value in data.items():
            dtype = str(value.dtype)
            if not self.convert_all:
                if dtype == DataDtypes.FLOAT64:
                    data[key] = value.astype(np.float32, copy=False)
            else:
                if dtype != DataDtypes.STRING:
                    data[key] = value.astype(np.float32, copy=False)
        return data

    def convert_to_float(self, data: ModelData) -> ModelData:
        if isinstance(data, pd.DataFrame):
            return self._convert_dataframe(data=data)
        if isinstance(data, np.ndarray):
            return self._convert_array(data=data)
        return self._convert_dict(data=data)
