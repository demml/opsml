from pathlib import Path
from typing import Optional

import numpy as np
import zarr

from opsml.registry.data.interfaces.base import DataInterface
from opsml.registry.types import AllowedDataType, Feature, Suffix


class NumpyData(DataInterface):
    data: Optional[np.ndarray] = None

    def save_data(self, path: Path) -> Path:
        """Saves numpy array as a zarr file"""
        save_path = path.with_suffix(Suffix.ZARR.value)
        zarr.save(save_path, self.data)

        self.feature_map = {
            "numpy_array": Feature(
                feature_type=str(self.data.dtype),
                shape=self.data.shape,
            )
        }

        return save_path

    def load_data(self, path: Path) -> None:
        """Load numpy array from zarr file"""
        load_path = path.with_suffix(Suffix.ZARR.value)
        self.data = zarr.load(load_path)

    @property
    def data_type(self) -> str:
        return AllowedDataType.NUMPY.value
