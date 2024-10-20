# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import tempfile
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Type, Union, cast

import joblib
from pydantic import BaseModel

from opsml.cards import (
    AuditCard,
    Card,
    DataCard,
    ModelCard,
    PipelineCard,
    ProjectCard,
    RunCard,
)
from opsml.data.interfaces._base import DataInterface
from opsml.data.interfaces.custom_data.base import Dataset
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import all_subclasses
from opsml.model.interfaces.base import ModelInterface
from opsml.model.interfaces.huggingface import HuggingFaceModel
from opsml.settings.config import config
from opsml.storage import client
from opsml.types import (
    AllowedDataType,
    CardType,
    CommonKwargs,
    RegistryTableNames,
    RegistryType,
    SaveName,
    Suffix,
)
from opsml.types.model import ModelMetadata, OnnxModel

logger = ArtifactLogger.get_logger()


class CardMap:
    @staticmethod
    def get_card(card_type: str) -> Type[Card]:
        if card_type == RegistryType.DATA.value:
            return DataCard
        if card_type == RegistryType.MODEL.value:
            return ModelCard
        if card_type == RegistryType.RUN.value:
            return RunCard
        if card_type == RegistryType.PIPELINE.value:
            return PipelineCard
        if card_type == RegistryType.AUDIT.value:
            return AuditCard
        if card_type == RegistryType.PROJECT.value:
            return ProjectCard
        raise ValueError(f"Card type {card_type} not found")


class CardLoadArgs(BaseModel):
    name: str
    repository: str
    version: str
    table_name: str

    @property
    def uri(self) -> Path:
        return Path(
            config.storage_root,
            self.table_name,
            self.repository,
            self.name,
            f"v{self.version}",
        )


def _get_data_interface(interface_type: str) -> DataInterface:
    """Load model interface from pathlib object

    Args:
        interface_type:
            Name of interface
    """
    interfaces = all_subclasses(DataInterface)
    interfaces.update(all_subclasses(Dataset))

    return next(
        (cls for cls in interfaces if cls.name() == interface_type),  # type: ignore
        DataInterface,  # type: ignore
    )


def _get_model_interface(interface_type: str) -> ModelInterface:
    """Load model interface from pathlib object

    Args:
        interface_type:
            Name of interface
    """

    return next(
        (cls for cls in all_subclasses(ModelInterface) if cls.name() == interface_type),  # type: ignore
        ModelInterface,  # type: ignore[arg-type]
    )


def get_interface(registry_type: RegistryType, interface_type: str) -> Union[ModelInterface, DataInterface]:
    """Gets model or data interfaces

    Args:
        registry_type:
            Registry type
        interface_type:
            Interface type

    Returns:
        Either ModelInterface or DataInterface
    """

    if registry_type == RegistryType.MODEL:
        return _get_model_interface(interface_type)
    return _get_data_interface(interface_type)


class CardLoader:
    def __init__(
        self,
        registry_type: RegistryType,
        card: Optional[Card] = None,
        card_args: Optional[Dict[str, Any]] = None,
    ):
        """
        Parent class for saving artifacts belonging to cards or loading cards.

        Args:
            card:
                Card with artifacts to save
            card_args:
                Card args to use to get remote path (injected during card loading)
            registry_type:
                Registry type to use. (For loading artifact cards)
        """

        self._card = card
        self.card_args = card_args
        self.registry_type = registry_type
        self.storage_client = client.storage_client

    @cached_property
    def card(self) -> Card:
        assert self._card is not None
        return self._card

    def get_rpath_from_args(self) -> Path:
        """Get remote path from card args"""

        table_name = RegistryTableNames.from_str(self.registry_type.value).value
        assert self.card_args is not None
        args = CardLoadArgs(**self.card_args, table_name=table_name)

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

    def _load_card_from_storage(self, rpath: Path) -> Dict[str, Any]:
        """Attempts to load pydantic card from storage. Newer versions of OpsML use JSON to save cards.
        Older versions use joblib. This method attempts to load from JSON first, then falls back to joblib.

        Args:
            rpath:
                Remote path to load file

        Returns:
            Loaded card
        """
        try:
            # load card from JSON
            with self._load_object(SaveName.CARD.value, Suffix.JSON.value, rpath) as lpath:
                with lpath.open(encoding="utf-8") as lfile:
                    return cast(Dict[str, Any], json.load(lfile))

        except IOError:  # pylint: disable=broad-except
            error = (
                "Error loading card JSON version of card. Falling back to joblib. "
                "Newer versions of OpsML use JSON to save cards. Older versions use joblib."
            )
            logger.error(error)
            try:
                with self._load_object(SaveName.CARD.value, Suffix.JOBLIB.value, rpath) as lpath:
                    return cast(Dict[str, Any], joblib.load(lpath))

            except IOError as joblib_error:  # pylint: disable=broad-except
                logger.error("Error loading card: {}", joblib_error)
                raise joblib_error

    def _load_dataset(self, rpath: Path) -> Dict[str, Any]:
        """Loads dataset from storage

        Args:
            interface:
                Dataset interface
            rpath:
                Remote path to load file
        """
        with self._load_object(SaveName.DATASET.value, Suffix.JOBLIB.value, rpath) as lpath:
            loaded_card: Dict[str, Any] = joblib.load(lpath)

        return loaded_card

    def load_card(self, interface: Optional[Union[Type[DataInterface], Type[ModelInterface]]] = None) -> Card:
        """Loads a Card from card arguments

        Returns:
            Loaded Card
        """
        rpath = self.get_rpath_from_args()
        loaded_card = self._load_card_from_storage(rpath)

        # load interface logic
        if self.registry_type in (RegistryType.MODEL, RegistryType.DATA):
            interface_type: str = loaded_card["metadata"]["interface_type"]

            if interface_type in [AllowedDataType.IMAGE.value, AllowedDataType.TEXT.value]:
                loaded_card["interface"] = self._load_dataset(rpath)

            if interface is not None:
                loaded_interface = interface.model_validate(loaded_card["interface"])

            else:
                interface = get_interface(self.registry_type, interface_type)
                loaded_interface = interface.model_validate(loaded_card["interface"])

            loaded_card["interface"] = loaded_interface

        return CardMap.get_card(self.registry_type)(**loaded_card)

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardLoader(CardLoader):
    """DataCard loader. Methods are meant to be called individually"""

    def __init__(
        self,
        card: Optional[DataCard] = None,
        card_args: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(RegistryType.DATA, card, card_args)
        self._card = card

    @cached_property
    def card(self) -> DataCard:
        assert isinstance(self._card, DataCard)
        return self._card

    @cached_property
    def data_suffix(self) -> str:
        assert isinstance(self.card.interface, DataInterface)
        return self.card.interface.data_suffix

    def _load_interface_data(self) -> None:
        assert isinstance(self.card.interface, DataInterface)

        if self.card.interface.data is not None:
            logger.info("Data already loaded")
            return

        with self._load_object(SaveName.DATA.value, self.data_suffix) as lpath:
            self.card.interface.load_data(lpath)

        return

    def _load_dataset_data(self, **kwargs: Union[str, int]) -> None:
        assert isinstance(self.card.interface, Dataset)

        split = kwargs.get("split")

        load_path = SaveName.DATA.value

        if split is not None:
            load_path = f"{load_path}/{split}"

        with self._load_object(load_path, Suffix.NONE.value) as lpath:
            self.card.interface.load_data(lpath, **kwargs)

    def load_data(self, **kwargs: Union[str, int]) -> None:
        """Saves a data via data interface"""

        if isinstance(self.card.interface, Dataset):
            return self._load_dataset_data(**kwargs)
        return self._load_interface_data()

    def load_data_profile(self) -> None:
        """Saves a data profile"""

        if isinstance(self.card.interface, Dataset):
            return

        if self.card.interface.data_profile is not None:
            logger.info("Data profile already loaded")
            return

        # check exists
        rpath = Path(self.card.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JSON.value)
        if not self.storage_client.exists(rpath):
            return

        # load data profile
        with self._load_object(SaveName.DATA_PROFILE.value, Suffix.JSON.value) as lpath:
            self.card.interface.load_data_profile(lpath)

        return

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelCardLoader(CardLoader):
    """ModelCard loader. Methods are meant to be called individually"""

    def __init__(
        self,
        card: Optional[ModelCard] = None,
        card_args: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(RegistryType.MODEL, card, card_args)
        self._card = card

    @cached_property
    def card(self) -> ModelCard:
        assert isinstance(self._card, ModelCard)
        return self._card

    @cached_property
    def model_suffix(self) -> str:
        return self.card.interface.model_suffix

    @cached_property
    def preprocessor_suffix(self) -> str:
        return cast(str, self.card.interface.preprocessor_suffix)

    @property
    def onnx_suffix(self) -> str:
        """Get onnx suffix to load file. HuggingFaceModel uses a directory path"""
        if not isinstance(self.card.interface, HuggingFaceModel):
            return Suffix.ONNX.value
        return ""

    def _load_data_interface(self) -> str:
        interface_type = self.card.interface.sample_data_interface_type
        # load sample data interface if it exists
        if interface_type != CommonKwargs.UNDEFINED.value:
            interface: DataInterface = get_interface(RegistryType.DATA, interface_type)()  # type: ignore
            interface.feature_map = self.card.interface.feature_map
            self.card.interface.sample_data = interface

            return interface.data_suffix

        return self.card.interface.data_suffix

    def _load_sample_data(self, lpath: Path, rpath: Path) -> None:
        """Load sample data for model interface. Sample data is is either saved in
        a DataInterface or joblib

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """
        if self.card.interface.sample_data is not None:
            logger.info("Sample data already loaded")
            return None

        data_suffix = self._load_data_interface()

        load_rpath = Path(self.card.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(data_suffix)
        if not self.storage_client.exists(load_rpath):
            return None

        lpath = self.download(lpath, rpath, SaveName.SAMPLE_MODEL_DATA.value, data_suffix)

        return self.card.interface.load_sample_data(lpath)

    def _load_onnx_config(self, lpath: Path, rpath: Path) -> None:
        """Load onnx config for huggingface models

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        load_rpath = Path(self.card.uri, SaveName.ONNX_CONFIG.value).with_suffix(Suffix.JOBLIB.value)
        if not self.storage_client.exists(load_rpath):
            return

        lpath = self.download(lpath, rpath, SaveName.ONNX_CONFIG.value, Suffix.JOBLIB.value)

        self.card.interface.onnx_args.config = joblib.load(lpath)

        return

    def _load_huggingface_preprocessors(self, lpath: Path, rpath: Path) -> None:
        """Loads huggingface tokenizer and feature extractors. Skips if already loaded or not found

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """
        assert isinstance(self.card.interface, HuggingFaceModel), "Expected HuggingFaceModel"

        if self.card.interface.tokenizer is None:
            load_rpath = Path(self.card.uri, SaveName.TOKENIZER.value)

            if self.storage_client.exists(load_rpath):
                lpath = self.download(lpath, rpath, SaveName.TOKENIZER.value, "")
                self.card.interface.load_tokenizer(lpath)
                return

        if self.card.interface.feature_extractor is None:
            load_rpath = Path(self.card.uri, SaveName.FEATURE_EXTRACTOR.value)
            if self.storage_client.exists(load_rpath):
                lpath = self.download(lpath, rpath, SaveName.FEATURE_EXTRACTOR.value, "")
                self.card.interface.load_feature_extractor(lpath)
                return

        return

    def load_preprocessor(self, lpath: Optional[Path] = None, rpath: Optional[Path] = None) -> None:
        """Load Preprocessor for model interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """
        if isinstance(self.card.interface, HuggingFaceModel):
            assert lpath is not None and rpath is not None
            self._load_huggingface_preprocessors(lpath, rpath)
            return

        if not hasattr(self.card.interface, "preprocessor"):
            return

        if self.card.interface.preprocessor is not None:
            logger.info("Preprocessor already loaded")
            return

        load_rpath = Path(self.card.uri, SaveName.PREPROCESSOR.value).with_suffix(self.preprocessor_suffix)
        if not self.storage_client.exists(load_rpath):
            return

        assert lpath is not None and rpath is not None
        lpath = self.download(lpath, rpath, SaveName.PREPROCESSOR.value, self.preprocessor_suffix)
        self.card.interface.load_preprocessor(lpath)
        return

    def _load_model(self, lpath: Path, rpath: Path, **kwargs: Any) -> None:
        """Load model to interface

        Args:
            lpath:
                Local path to save file
            rpath:
                Remote path to load file
        """

        lpath = self.download(lpath, rpath, SaveName.TRAINED_MODEL.value, self.model_suffix)
        self.card.interface.load_model(lpath, **kwargs)

        if isinstance(self.card.interface, HuggingFaceModel):
            if self.card.interface.is_pipeline:
                self.card.interface.to_pipeline()

    def _load_huggingface_onnx_model(self, lpath: Path, rpath: Path, load_quantized: bool) -> None:
        """Load onnx model to interface

        Args:
            kwargs:
                Kwargs to pass for onnx loading
        """

        # check for hf model and what type of onnx to load
        assert isinstance(self.card.interface, HuggingFaceModel), "Expected HuggingFaceModel"
        save_name = SaveName.QUANTIZED_MODEL.value if load_quantized else SaveName.ONNX_MODEL.value

        load_rpath = Path(rpath, save_name)
        if not self.storage_client.exists(load_rpath):
            logger.info("No onnx model exists for {}", load_rpath.as_posix())
            return

        if self.card.interface.is_pipeline:
            self._load_huggingface_preprocessors(lpath, rpath)

        # download and load onnx model
        load_path = self.download(lpath, rpath, save_name, "")
        self.card.interface.onnx_model = OnnxModel(onnx_version=self.card.metadata.data_schema.onnx_version)
        self.card.interface.load_onnx_model(load_path)

        # load onnx config
        self._load_onnx_config(lpath, rpath)

        return

    def _load_onnx_model(self, lpath: Path, rpath: Path, load_quantized: bool) -> None:
        """Load onnx model to interface

        Args:
            kwargs:
                Kwargs to pass for onnx loading
        """

        if self.card.interface.onnx_model is not None:
            logger.info("Onnx model already loaded")
            return

        if isinstance(self.card.interface, HuggingFaceModel):
            self._load_huggingface_onnx_model(lpath, rpath, load_quantized)
            return

        save_name = SaveName.ONNX_MODEL.value
        if not self.storage_client.exists(Path(rpath, save_name).with_suffix(self.onnx_suffix)):
            logger.info("No onnx model exists for {}", save_name)
            return

        load_lpath = self.download(lpath, rpath, save_name, self.onnx_suffix)
        self.card.interface.onnx_model = OnnxModel(onnx_version=self.card.metadata.data_schema.onnx_version)
        self.card.interface.load_onnx_model(load_lpath)
        return

    def load_model_metadata(self) -> ModelMetadata:
        """Load model metadata to interface"""

        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri
            load_path = self.download(lpath, rpath, SaveName.MODEL_METADATA.value, Suffix.JSON.value)

            with load_path.open(encoding="utf-8") as json_file:
                metadata = json.load(json_file)

        return ModelMetadata(**metadata)

    def load_onnx_model(self, load_preprocessor: bool = False, load_quantized: bool = False) -> None:
        if self.card.interface.onnx_model is not None:
            logger.info("Onnx Model already loaded")
            return None

        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri

            if load_preprocessor:
                self.load_preprocessor(lpath, rpath)

            self._load_onnx_model(lpath, rpath, load_quantized)

        return None

    def load_model(self, load_preprocessor: bool, **kwargs: Any) -> None:
        """Load model, preprocessor and sample data"""

        if self.card.interface.model is not None:
            logger.info("Model already loaded")
            return None

        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri

            if load_preprocessor:
                self.load_preprocessor(lpath, rpath)

            self._load_sample_data(lpath, rpath)
            self._load_model(lpath, rpath, **kwargs)

        return None

    def _download_preprocessor(self, metadata: ModelMetadata, lpath: Path) -> None:
        """Helper method for downloading preprocessor

        Args:
            metadata:
                Model metadata
            lpath:
                Local path to save file
        """

        if isinstance(self.card.interface, HuggingFaceModel):
            if getattr(metadata, "tokenizer_uri", None) is not None:
                rpath = Path(metadata.tokenizer_uri)
                _lpath = (lpath / rpath.name).with_suffix("")

            if getattr(metadata, "feature_extractor_uri", None) is not None:
                rpath = Path(metadata.feature_extractor_uri)
                _lpath = (lpath / rpath.name).with_suffix("")
        else:
            if getattr(metadata, "preprocessor_uri", None) is not None:
                rpath = Path(metadata.preprocessor_uri)
                _lpath = (lpath / rpath.name).with_suffix(self.preprocessor_suffix)
            else:
                raise ValueError("Preprocessor uri is not set in metadata. Was a preprocessor created?")

        if _lpath.suffix == "":
            _lpath.mkdir(parents=True, exist_ok=True)
        self.storage_client.get(rpath, _lpath)

    def _download_onnx_model(self, metadata: ModelMetadata, lpath: Path, load_quantized: bool) -> None:
        """Download onnx model

        Args:
            metadata:
                Model metadata
            lpath:
                Local path to save file
            quantize:
                Whether to download quantized model
        """

        if load_quantized:
            assert hasattr(
                metadata, "quantized_model_uri"
            ), "Quantized model uri is not set in metadata. Was an onnx model quantized?"
            rpath = Path(metadata.quantized_model_uri)
        else:
            assert metadata.onnx_uri is not None, "Onnx model uri is not set in metadata. Was an onnx model created?"
            rpath = Path(metadata.onnx_uri)

        _lpath = (lpath / rpath.name).with_suffix(self.onnx_suffix)

        if _lpath.suffix == "":
            _lpath.mkdir(parents=True, exist_ok=True)

        self.storage_client.get(rpath, _lpath)

    def _download_model(self, metadata: ModelMetadata, lpath: Path) -> None:
        """Download model

        Args:
            metadata:
                Model metadata
            lpath:
                Local path to save file
        """
        rpath = Path(metadata.model_uri)
        _lpath = (lpath / rpath.name).with_suffix(self.model_suffix)

        if _lpath.suffix == "":
            _lpath.mkdir(parents=True, exist_ok=True)

        self.storage_client.get(rpath, _lpath)

    def download_model(
        self,
        lpath: Path,
        load_preprocessor: bool = False,
        load_onnx: bool = False,
        load_quantized: bool = False,
    ) -> None:
        """Download model and metadata

        Args:
            lpath:
                Local path to save file
            load_preprocessor:
                Whether to load preprocessor or not. Default is False
            load_onnx:
                Whether to load onnx model or not. Default is False
            load_quantized:
                Whether to load quantized model or not. Default is False
        """

        lpath.mkdir(parents=True, exist_ok=True)
        rpath = self.card.uri

        # load metadata
        metadata = self.load_model_metadata()

        # download preprocessor
        if load_preprocessor:
            self._download_preprocessor(metadata, lpath)

        if load_onnx:
            self._download_onnx_model(metadata, lpath, load_quantized)

        else:
            # download model
            self._download_model(metadata, lpath)

        # download metadata
        self.download(lpath, rpath, SaveName.MODEL_METADATA.value, Suffix.JSON.value)

    def load_drift_profile(self) -> None:
        """Load drift profile to interface"""

        if self.card.interface.drift_profile is not None:
            logger.info("Drift profile already loaded")
            return

        rpath = Path(self.card.uri, SaveName.DRIFT_PROFILE.value).with_suffix(Suffix.JSON.value)
        if not self.storage_client.exists(rpath):
            return

        with self._load_object(SaveName.DRIFT_PROFILE.value, Suffix.JSON.value) as lpath:
            self.card.interface.load_drift_profile(lpath)

        return

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type
