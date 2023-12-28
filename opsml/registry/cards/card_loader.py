# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import tempfile
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Iterator, cast

import joblib
from pydantic import BaseModel

from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.data import DataCard
from opsml.registry.cards.model import ModelCard
from opsml.registry.model.interfaces.huggingface import HuggingFaceModel
from opsml.registry.storage import client
from opsml.registry.types import (
    CardType,
    RegistryTableNames,
    RegistryType,
    SaveName,
    Suffix,
)
from opsml.settings.config import config


class CardArgs(BaseModel):
    name: str
    team: str
    version: str
    table_name: str

    @property
    def uri(self) -> Path:
        return Path(config.storage_root, self.table_name, self.team, self.name, f"v{self.version}")


class CardLoader:
    def __init__(self, card: ArtifactCard):
        """
        Parent class for saving artifacts belonging to cards.
        ArtifactSaver controls pathing for all card objects

        Args:
            card:
                ArtifactCard with artifacts to save
            card_storage_info:
                Extra info to use with artifact storage
        """

        self._card = card
        self.storage_client = client.storage_client

    @cached_property
    def card(self) -> ArtifactCard:
        return self.card

    @cached_property
    def storage_suffix(self) -> str:
        return self.card.interface.storage_suffix

    @staticmethod
    def get_rpath_from_args(card_args: Dict[str, Any], registry_type: RegistryType) -> Path:
        """Get remote path from card args

        Args:
            card_args:
                Card args to use to get remote path
            registry_type:
                Registry type to use to get remote path
        Returns:
            Remote path
        """

        table_name = RegistryTableNames.from_str(registry_type.value).value
        args = CardArgs(**card_args, table_name=table_name)

        return args.uri

    @staticmethod
    def download(
        lpath: Path,
        rpath: Path,
        object_path: str,
        suffix: str,
        storage_client: client.StorageClientBase,
    ) -> Path:
        """Download file from rpath to lpath

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
            object_path:
                Path to object to load
            suffix:
                Suffix to add to object_path
            storage_client:
                Storage client to use
        """
        load_lpath = Path(lpath, object_path).with_suffix(suffix)
        load_rpath = Path(rpath, object_path).with_suffix(suffix)

        storage_client.get(load_rpath, load_lpath)

        return load_lpath

    @contextmanager
    def _load_object(self, object_path: str, suffix: str) -> Iterator[Path]:
        """Loads object from server storage to local path

        Args:
            object_path:
                Path to object to load
            suffix:
                Suffix to add to object_path
        Returns:
            Path to downloaded_object
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri

            yield self.download(lpath, rpath, object_path, suffix, self.storage_client)

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardLoader(CardLoader):
    """DataCard loader. Methods are meant to be called individually"""

    @cached_property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def load_data(self) -> None:
        """Saves a data via data interface"""

        if self.card.interface.data is not None:
            return None

        with self._load_object(SaveName.DATA.value, self.storage_suffix) as lpath:
            self.card.interface.load_data(lpath)

    def load_data_profile(self) -> None:
        """Saves a data profile"""

        # check exists
        rpath = Path(self.card.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JOBLIB.value)
        if not self.storage_client.exists(rpath):
            return None

        # load data profile
        with self._load_object(SaveName.DATA_PROFILE.value, Suffix.JOBLIB.value) as lpath:
            self.card.interface.load_profile(lpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelCardLoader(CardLoader):
    """ModelCard loader. Methods are meant to be called individually"""

    @cached_property
    def card(self) -> ModelCard:
        return cast(ModelCard, self._card)

    @property
    def onnx_suffix(self) -> str:
        """Get onnx suffix to load file. HuggingFaceModel uses a directory path"""
        if not isinstance(self.card.interface, HuggingFaceModel):
            return Suffix.ONNX.value
        return ""

    def _load_sample_data(self, lpath: Path, rpath: Path) -> None:
        """Load sample data for model interface. Sample data is always saved via joblib

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        load_rpath = Path(self.card.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
        if not self.storage_client.exists(load_rpath):
            return None

        lpath = self.download(lpath, rpath, SaveName.SAMPLE_MODEL_DATA.value, Suffix.JOBLIB.value, self.storage_client)

        self.card.interface.load_sample_data(lpath)

    def _load_preprocessor(self, lpath: Path, rpath: Path) -> None:
        """Load Preprocessor for model interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        load_rpath = Path(self.card.uri, SaveName.PREPROCESSOR.value).with_suffix(self.storage_suffix)
        if not self.storage_client.exists(load_rpath):
            return None

        lpath = self.download(lpath, rpath, SaveName.PREPROCESSOR.value, self.storage_suffix, self.storage_client)
        self.card.interface.load_preprocessor(lpath)

    def _load_model(self, lpath: Path, rpath: Path, **kwargs) -> None:
        """Load model to interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        if self.card.interface.model is not None:
            return None

        lpath = self.download(lpath, rpath, SaveName.TRAINED_MODEL.value, self.storage_suffix)
        self.card.interface.load_model(lpath, **kwargs)

    def load_onnx_model(self) -> None:
        """Load onnx model to interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        if self.card.interface.onnx_model is not None:
            return None

        load_rpath = Path(self.card.uri, SaveName.ONNX_MODEL.value).with_suffix(self.onnx_suffix)
        if not self.storage_client.exists(load_rpath):
            return None

        # onnx model is loaded separately
        with self._load_object(SaveName.ONNX_MODEL.value, self.onnx_suffix) as lpath:
            self.card.interface.load_onnx_model(lpath)

    def load_model(self) -> None:
        """Load model, preprocessor and sample data"""

        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri
            self._load_model(lpath, rpath)
            self._load_preprocessor(lpath, rpath)
            self._load_sample_data(lpath, rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type


def load_card_from_record(card_record: Dict[str, Any], registry_type: RegistryType) -> None:
    """Load card from record

    Args:
        card:
            Card to load
    """
    # this should be part of the actual loader
    # start here tomorrow
    rpath = CardLoader.get_rpath_from_args(card_record, registry_type)
    with tempfile.TemporaryDirectory() as tmp_dir:
        lpath = Path(tmp_dir)
        rpath = CardLoader.get_rpath_from_args(card_record, registry_type)
        load_path = CardLoader.download(lpath, rpath, SaveName.CARD.value, Suffix.JOBLIB.value, client.storage_client)
        loaded_card: Dict[str, Any] = joblib.load(load_path)

        if registry_type == RegistryType.MODEL or registry_type == RegistryType.DATA:
            # load interface
            interface_type: str = loaded_card["metadata"]["interface_type"]

            # get interface type
