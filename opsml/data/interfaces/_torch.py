from pathlib import Path
from typing import Optional, Union

from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, Feature, Suffix

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

        def save_data(self, path: Path) -> None:
            """Saves torch dataset or tensor(s)"""

            assert self.data is not None, "No data detected in interface"

            torch.save(self.data, path)

            if isinstance(self.data, Dataset):
                assert hasattr(self.data, "data"), "Dataset must have attribute data"
                shape = self.data.data.shape
                dtype = str(self.data.data.dtype)

            else:
                shape = self.data.shape
                dtype = str(self.data.dtype)

            self.feature_map = {"features": Feature(feature_type=dtype, shape=shape)}

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
    from typing import Any, Dict

    from pydantic import model_validator

    class TorchData(DataInterface):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError("TorchData requires pytorch to be installed. Please install pytorch.")

        @staticmethod
        def name() -> str:
            return TorchData.__name__
