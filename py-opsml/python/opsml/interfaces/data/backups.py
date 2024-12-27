from pathlib import Path
from typing import Any, Dict, Union

from opsml.interfaces.data.base import DataInterface
from opsml.interfaces.data.file_system.base import Dataset
from pydantic import model_validator


class TorchDataNoModule(DataInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("TorchData requires pytorch to be installed. Please install pytorch.")

    @staticmethod
    def name() -> str:
        return TorchDataNoModule.__name__


class ImageDatasetNoModule(Dataset):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("ImageDataset requires pillow to be installed. Please install pillow.")

    @staticmethod
    def name() -> str:
        return ImageDatasetNoModule.__name__

    def split_data(self) -> None:
        """Creates data splits based on subdirectories of data_dir and supplied split value

        Returns:
            None
        """
        raise NotImplementedError

    def save_data(self, path: Path) -> None:
        """Saves data to data_dir

        Args:
            path:
                Path to save data

        """
        raise NotImplementedError

    def load_data(self, path: Path, **kwargs: Union[int, str]) -> None:
        """Saves data to data_dir

        Args:
            path:
                Path to save data

            kwargs:
                Keyword arguments to pass to the data loader

        """
        raise NotImplementedError
