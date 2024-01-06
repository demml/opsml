# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import tempfile
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, cast
from venv import logger

import joblib
from pydantic import BaseModel

from opsml.cards import (
    ArtifactCard,
    AuditCard,
    DataCard,
    ModelCard,
    PipelineCard,
    ProjectCard,
    RunCard,
)
from opsml.data.interfaces import get_data_interface
from opsml.model.interfaces import HuggingFaceModel, get_model_interface
from opsml.settings.config import config
from opsml.storage import client
from opsml.types import CardType, RegistryTableNames, RegistryType, SaveName, Suffix
from opsml.types.model import ModelMetadata, OnnxModel

table_name_card_map = {
    RegistryType.DATA.value: DataCard,
    RegistryType.MODEL.value: ModelCard,
    RegistryType.RUN.value: RunCard,
    RegistryType.PIPELINE.value: PipelineCard,
    RegistryType.AUDIT.value: AuditCard,
    RegistryType.PROJECT.value: ProjectCard,
}


class CardLoadArgs(BaseModel):
    name: str
    team: str
    version: str
    table_name: str
    storage_root: str

    @property
    def uri(self) -> Path:
        return Path(
            self.storage_root,
            self.table_name,
            self.team,
            self.name,
            f"v{self.version}",
        )


class CardLoader:
    def __init__(
        self,
        card: Optional[ArtifactCard] = None,
        card_args: Optional[Dict[str, Any]] = None,
        registry_type: Optional[RegistryType] = None,
        storage_client: Optional[client.StorageClient] = None,
    ):
        """
        Parent class for saving artifacts belonging to cards or loading cards.

        Args:
            card:
                ArtifactCard with artifacts to save
            card_args:
                Card args to use to get remote path (injected during card loading)
            registry_type:
                Registry type to use. (For loading artifact cards)
        """

        self._card = card
        self.card_args = card_args
        self.registry_type = registry_type
        self.storage_client = storage_client or client.storage_client

    @cached_property
    def card(self) -> ArtifactCard:
        assert self._card is not None
        return self._card

    def get_rpath_from_args(self) -> Path:
        """Get remote path from card args"""

        table_name = RegistryTableNames.from_str(self.registry_type.value).value
        args = CardLoadArgs(
            **self.card_args,
            table_name=table_name,
            storage_root=config.get_storage_root(self.storage_client.settings.storage_system.value),
        )

        return args.uri

    def download(
        self,
        lpath: Path,
        rpath: Path,
        object_path: str,
        suffix: str,
    ) -> Path:
        """Download file from rpath to lpath

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
            object_path:
                Path of object to load
            suffix:
                Suffix to add to object_path
            storage_client:
                Storage client to use
        """

        load_lpath = Path(lpath, object_path).with_suffix(suffix)
        load_rpath = Path(rpath, object_path).with_suffix(suffix)

        self.storage_client.get(load_rpath, load_lpath)
        return load_lpath

    @contextmanager
    def _load_object(
        self,
        object_path: str,
        suffix: str,
        rpath: Optional[Path] = None,
    ) -> Iterator[Path]:
        """Loads object from server storage to local path

        Args:
            object_path:
                Path to object to load
            suffix:
                Suffix to add to object_path
            rpath:
                Remote path to load file

        Returns:
            Path to downloaded_object
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = rpath or self.card.uri

            yield self.download(lpath, rpath, object_path, suffix)

    def load_card(self) -> ArtifactCard:
        """Loads an ArtifactCard from card arguments

        Returns:
            Loaded ArtifactCard
        """
        rpath = self.get_rpath_from_args()

        with self._load_object(SaveName.CARD.value, Suffix.JOBLIB.value, rpath) as lpath:
            loaded_card: Dict[str, Any] = joblib.load(lpath)

        # load interface logic
        if self.registry_type == RegistryType.MODEL or self.registry_type == RegistryType.DATA:
            # get interface type
            interface_type: str = loaded_card["metadata"]["interface_type"]

            if self.registry_type == RegistryType.MODEL:
                interface = get_model_interface(interface_type)
            else:
                interface = get_data_interface(interface_type)

            loaded_interface = interface(**loaded_card["interface"])
            loaded_card["interface"] = loaded_interface

        return cast(ArtifactCard, table_name_card_map[self.registry_type.value](**loaded_card))

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardLoader(CardLoader):
    """DataCard loader. Methods are meant to be called individually"""

    @cached_property
    def card(self) -> DataCard:
        assert isinstance(self._card, DataCard)
        return self._card

    @cached_property
    def data_suffix(self) -> str:
        return self.card.interface.data_suffix

    def load_data(self) -> None:
        """Saves a data via data interface"""

        if self.card.interface.data is not None:
            logger.info("Data already loaded")
            return None

        with self._load_object(SaveName.DATA.value, self.data_suffix) as lpath:
            self.card.interface.load_data(lpath)

    def load_data_profile(self) -> None:
        """Saves a data profile"""

        if self.card.interface.data_profile is not None:
            logger.info("Data profile already loaded")
            return None

        # check exists
        rpath = Path(self.card.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JOBLIB.value)
        if not self.storage_client.exists(rpath):
            return None

        # load data profile
        with self._load_object(SaveName.DATA_PROFILE.value, Suffix.JOBLIB.value) as lpath:
            self.card.interface.load_data_profile(lpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelCardLoader(CardLoader):
    """ModelCard loader. Methods are meant to be called individually"""

    @cached_property
    def card(self) -> ModelCard:
        assert isinstance(self._card, ModelCard)
        return self._card

    @cached_property
    def model_suffix(self) -> str:
        return self.card.interface.model_suffix

    @cached_property
    def preprocessor_suffix(self) -> str:
        return self.card.interface.preprocessor_suffix

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
        if self.card.interface.sample_data is not None:
            logger.info("Sample data already loaded")
            return None

        load_rpath = Path(self.card.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
        if not self.storage_client.exists(load_rpath):
            return None

        lpath = self.download(lpath, rpath, SaveName.SAMPLE_MODEL_DATA.value, Suffix.JOBLIB.value)

        self.card.interface.load_sample_data(lpath)

    def _load_preprocessor(self, lpath: Path, rpath: Path) -> None:
        """Load Preprocessor for model interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        if self.card.interface.preprocessor is not None:
            logger.info("Preprocessor already loaded")
            return None

        load_rpath = Path(self.card.uri, SaveName.PREPROCESSOR.value).with_suffix(self.preprocessor_suffix)
        if not self.storage_client.exists(load_rpath):
            logger.info("Onnx model already loaded")
            return None

        lpath = self.download(lpath, rpath, SaveName.PREPROCESSOR.value, self.preprocessor_suffix)
        self.card.interface.load_preprocessor(lpath)

    def _load_model(self, lpath: Path, rpath: Path, **kwargs: Dict[str, Any]) -> None:
        """Load model to interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        lpath = self.download(lpath, rpath, SaveName.TRAINED_MODEL.value, self.model_suffix)
        self.card.interface.load_model(lpath, **kwargs)

    def load_onnx_model(self, load_quantized: bool = False) -> None:
        """Load onnx model to interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        save_name = SaveName.QUANTIZED_MODEL.value if load_quantized else SaveName.ONNX_MODEL.value
        if self.card.interface.onnx_model is not None:
            logger.info("Onnx model already loaded")
            return None

        load_rpath = Path(self.card.uri, save_name).with_suffix(self.onnx_suffix)
        if not self.storage_client.exists(load_rpath):
            logger.info("No onnx model exists for {}", save_name)
            return None

        with self._load_object(save_name, self.onnx_suffix) as lpath:
            self.card.interface.onnx_model = OnnxModel(onnx_version=self.card.metadata.data_schema.onnx_version)
            self.card.interface.load_onnx_model(lpath)

    def load_model_metadata(self) -> ModelMetadata:
        """Load model metadata to interface"""

        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri
            load_path = self.download(lpath, rpath, SaveName.MODEL_METADATA.value, Suffix.JSON.value)

            with load_path.open() as json_file:
                metadata = json.load(json_file)

        return ModelMetadata(**metadata)

    def load_model(self, **kwargs: Dict[str, Any]) -> None:
        """Load model, preprocessor and sample data"""

        if self.card.interface.model is not None:
            logger.info("Model already loaded")
            return None

        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri
            self._load_model(lpath, rpath, **kwargs)
            self._load_preprocessor(lpath, rpath)
            self._load_sample_data(lpath, rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type
