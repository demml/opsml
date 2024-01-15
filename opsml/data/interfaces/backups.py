from typing import Any, Dict

from pydantic import model_validator

from opsml.data.interfaces._base import DataInterface
from opsml.data.interfaces.custom_data import Dataset


class TorchDataNoModule(DataInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("TorchData requires pytorch to be installed. Please install pytorch.")

    @staticmethod
    def name() -> str:
        return TorchDataNoModule.__name__


class ImageDataNoModule(Dataset):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("ImageData requires pillow to be installed. Please install pillow.")

    @staticmethod
    def name() -> str:
        return ImageDataNoModule.__name__
