from pathlib import Path
from typing import Any, Optional

import numpy as np
from opsml import DataType
from opsml.interfaces.data.base import DataInterface
from opsml.interfaces.data.features.formatter import generate_feature_schema


class NumpyData(DataInterface):
    """Numpy data interface

    Args:
        data:
            Numpy array
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

    data: Optional[np.ndarray[Any, Any]] = None

    def save_data(self, path: Path) -> None:
        """Saves numpy array as a zarr file"""

        assert self.data is not None, "No data detected in interface"

        # same numpy array
        np.save(path, self.data)

        self.feature_map = generate_feature_schema(self.data, self.data_type)

    def load_data(self, path: Path) -> None:
        """Load numpy array from zarr file"""

        self.data = np.load(path)

    @property
    def data_type(self) -> DataType:
        return DataType.Numpy

    @staticmethod
    def name() -> str:
        return NumpyData.__name__
