from typing import Any, Dict

from pydantic import model_validator

from opsml.data.interfaces._base import DataInterface
from opsml.types import AllowedDataType


class TorchDataNoModule(DataInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("TorchData requires pytorch to be installed. Please install pytorch.")

    @staticmethod
    def name() -> str:
        return TorchDataNoModule.__name__

    @property
    def data_type(self) -> str:
        return AllowedDataType.TORCH_TENSOR.value
