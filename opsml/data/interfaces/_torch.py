from pathlib import Path
from typing import Optional

from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType, Feature, Suffix

try:
    import torch

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
            is_dataset:
                Whether data is a torch dataset or not
        """

        data: Optional[torch.Tensor] = None

        def save_data(self, path: Path) -> None:
            """Saves torch dataset or tensor(s)"""

            assert self.data is not None, "No data detected in interface"

            torch.save(self.data, path)
            self.feature_map["features"] = Feature(feature_type=str(self.data.dtype), shape=self.data.shape)

        def load_data(self, path: Path) -> None:
            """Load torch tensors or torch datasets"""
            self.data = torch.load(path)

        @property
        def data_type(self) -> str:
            return AllowedDataType.TORCH_TENSOR.value

        @property
        def data_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.PT.value

        @staticmethod
        def name() -> str:
            return TorchData.__name__

except ModuleNotFoundError:
    from opsml.data.interfaces.backups import TorchDataNoModule as TorchData
