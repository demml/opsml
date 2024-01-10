from pathlib import Path
from typing import Any, Optional

import numpy as np
import zarr

from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, Feature, Suffix


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

        zarr.save(path, self.data)

        self.feature_map = {
            "features": Feature(
                feature_type=str(self.data.dtype),
                shape=self.data.shape,
            )
        }

    def load_data(self, path: Path) -> None:
        """Load numpy array from zarr file"""

        self.data = zarr.load(path)

    @property
    def data_type(self) -> str:
        return AllowedDataType.NUMPY.value

    @property
    def data_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.ZARR.value

    @staticmethod
    def name() -> str:
        return NumpyData.__name__
