from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, CommonKwargs, Feature, Suffix

try:
    import torch
    from torch.utils.data import Dataset

    class TorchData(DataInterface):
        """Torch dataset interface

        Args:
            data:
                Torch dataset or torch tensors
            dependent_vars:
                List of dependent variables. Can be string or index if using numpy
            data_splits:
                Optional list of `DataSplit`
            feature_map:
                Dictionary of features -> automatically generated
            feature_descriptions:
                Dictionary or feature descriptions
            sql_logic:
                Sql logic used to generate data
        """

        data: Optional[Union[Dataset, torch.Tensor]] = None

        def _add_feature(self, name: str, shape: Tuple[Any, ...], dtype: str) -> None:
            self.feature_map[name] = Feature(feature_type=dtype, shape=shape)

        def save_data(self, path: Path) -> None:
            """Saves torch dataset or tensor(s)"""

            assert self.data is not None, "No data detected in interface"

            torch.save(self.data, path)

            if isinstance(self.data, Dataset):
                sample = self.data.__getitem__(0)

                if isinstance(sample, (tuple, list)):
                    for nbr, _sample in enumerate(sample):
                        self._add_feature(name=f"features_{nbr}", shape=_sample.shape, dtype=str(_sample.dtype))

                elif isinstance(sample, dict):
                    for key, _sample in sample.items():
                        self._add_feature(name=str(key), shape=_sample.shape, dtype=str(_sample.dtype))

                else:
                    try:
                        self._add_feature("features", sample.shape, str(sample.dtype))
                    except Exception:
                        self._add_feature("features", (CommonKwargs.UNDEFINED.value), CommonKwargs.UNDEFINED.value)

            else:
                self._add_feature("features", self.data.shape, str(self.data.dtype))

        def load_data(self, path: Path) -> None:
            """Load numpy array from zarr file"""
            self.data = torch.load(path)

        @property
        def data_type(self) -> str:
            if isinstance(self.data, Dataset):
                return AllowedDataType.TORCH_DATASET.value
            return AllowedDataType.TORCH_TENSOR.value

        @property
        def data_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.PT.value

        @staticmethod
        def name() -> str:
            return TorchData.__name__

except ModuleNotFoundError:
    from pydantic import model_validator

    class TorchData(DataInterface):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError("TorchData requires pytorch to be installed. Please install pytorch.")

        @staticmethod
        def name() -> str:
            return TorchData.__name__
