# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import UUID

from pydantic import ConfigDict, SerializeAsAny, field_validator
from scouter import SpcDriftProfile

from opsml.cards.base import ArtifactCard
from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.base import ModelInterface
from opsml.types import (
    CardType,
    ModelCardMetadata,
    ModelMetadata,
    OnnxModel,
    SaveName,
    Suffix,
)

logger = ArtifactLogger.get_logger()


class ModelCard(ArtifactCard):
    """Create a ModelCard from your trained machine learning model.
    This Card is used in conjunction with the ModelCardCreator class.

    Args:
        interface:
                Trained model interface.
        name:
            Name for the model specific to your current project
        repository:
            Repository that this model is associated with
        contact:
            Contact to associate with card
        info:
            `CardInfo` object containing additional metadata. If provided, it will override any
            values provided for `name`, `repository`, `contact`, and `version`.

            Name, repository, and contact are required arguments for all cards. They can be provided
            directly or through a `CardInfo` object.

        uid:
            Unique id (assigned if card has been registered)
        version:
            Current version (assigned if card has been registered)
        datacard_uid:
            Uid of the DataCard associated with training the model
        to_onnx:
            Whether to convert the model to onnx or not
        metadata:
            `ModelCardMetadata` associated with the model
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        protected_namespaces=("protect_",),
        validate_assignment=True,
        extra="forbid",
    )

    interface: SerializeAsAny[ModelInterface]
    datacard_uid: Optional[str] = None
    to_onnx: bool = False
    metadata: ModelCardMetadata = ModelCardMetadata()

    @field_validator("datacard_uid", mode="before")
    @classmethod
    def check_uid(cls, datacard_uid: Optional[str] = None) -> Optional[str]:
        if datacard_uid is None:
            return datacard_uid

        try:
            UUID(datacard_uid, version=4)  # we use uuid4
            return datacard_uid

        except ValueError as exc:
            raise ValueError("Datacard uid is not a valid uuid") from exc

    def load_model(self, load_preprocessor: bool = False, **kwargs: Any) -> None:
        """Loads model, preprocessor and sample data to interface

        Args:
            load_preprocessor:
                Whether to load preprocessor or not. Default is False

            **kwargs:
                additional kwargs to pass depending on the model type

                By default, all kwargs are passed to the framework specific loader
                e.g. torch.load(path, **kwargs)

                ### Opsml custom kwargs

                - In some instances the model architecture will be required when loading a model state.
                This is sometimes the case for torch, tensorflow and huggingface models.
                - If you need to load the model into a custom architecture use the
                `model_arch` kwarg (e.g. card.load_model(model_arch=my_custom_arch))
        """
        # load modelcard loader
        from opsml.storage.card_loader import ModelCardLoader

        ModelCardLoader(self).load_model(load_preprocessor, **kwargs)

    def download_drift_profile(self, path: Path) -> None:
        """Downloads drift profile to path

        Args:
            path:
                Path to download drift profile
        """

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        elif not path.is_dir():
            raise ValueError(f"The path {path} exists but is not a directory.")

        profile = self.load_drift_profile()

        if profile is None:
            logger.info("No drift profile found")
            return

        write_path = (path / SaveName.DRIFT_PROFILE.value).with_suffix(Suffix.JSON.value)

        profile.save_to_json(write_path)

    def download_model_metadata(self, path: Path) -> None:
        """Downloads model metadata to path

        Args:
            path:
                Path to download model metadata. Should be a directory path
        """
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        elif not path.is_dir():
            raise ValueError(f"The path {path} exists but is not a directory.")

        metadata = self.model_metadata
        metadata = metadata.model_dump_json()

        write_path = (path / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)

        # write json
        with write_path.open("w", encoding="utf-8") as file_:
            json.dump(metadata, file_)

    def download_model(
        self,
        path: Path,
        load_preprocessor: bool = False,
        load_onnx: bool = False,
        load_quantized: bool = False,
    ) -> None:
        """Downloads model, preprocessor and metadata to path

        Args:
            path:
                Path to download model
            load_preprocessor:
                Whether to load preprocessor or not. Default is False
            load_onnx:
                Whether to load onnx model or not. Default is False
            load_quantized:
                Whether to load quantized model or not. Default is False

        """

        from opsml.storage.card_loader import ModelCardLoader

        ModelCardLoader(self).download_model(
            lpath=path,
            load_preprocessor=load_preprocessor,
            load_onnx=load_onnx,
            load_quantized=load_quantized,
        )

    def load_onnx_model(self, load_preprocessor: bool = False, load_quantized: bool = False) -> None:
        """Loads onnx model to interface

        Args:
            load_preprocessor:
                Whether to load preprocessor or not. Default is False

            load_quantized:
                Whether to load quantized model or not. Default is False

        """

        from opsml.storage.card_loader import ModelCardLoader

        ModelCardLoader(self).load_onnx_model(load_preprocessor, load_quantized)

    def load_preprocessor(self, lpath: Optional[Path] = None, rpath: Optional[Path] = None) -> None:
        """Loads onnx model to interface

        Args:
            lpath (optional):
                Local path to load preprocessor from
            rpath (optional):
                Remote path to load preprocessor from

        """

        if self.preprocessor is not None:
            return

        from opsml.storage.card_loader import ModelCardLoader

        if lpath is None and rpath is None:
            with tempfile.TemporaryDirectory() as tmp_dir:
                lpath = Path(tmp_dir)
                rpath = self.uri
                ModelCardLoader(self).load_preprocessor(lpath, rpath)

        else:
            ModelCardLoader(self).load_preprocessor(lpath, rpath)

    def create_registry_record(self) -> Dict[str, Any]:
        """Creates a registry record from the current ModelCard"""

        exclude_vars = {"interface": {"model", "preprocessor", "sample_data", "onnx_model"}}
        dumped_model = self.model_dump(exclude=exclude_vars)
        dumped_model["interface_type"] = self.interface.name()
        dumped_model["task_type"] = self.interface.task_type

        return dumped_model

    @property
    def model(self) -> Any:
        """Quick access to model from interface"""
        return self.interface.model

    @property
    def sample_data(self) -> Any:
        """Quick access to sample data from interface"""
        return self.interface.sample_data

    @property
    def preprocessor(self) -> Any:
        """Quick access to preprocessor from interface"""

        if hasattr(self.interface, "preprocessor"):
            return self.interface.preprocessor

        if hasattr(self.interface, "tokenizer"):
            if self.interface.tokenizer is not None:
                return self.interface.tokenizer

        if hasattr(self.interface, "feature_extractor"):
            if self.interface.feature_extractor is not None:
                return self.interface.feature_extractor

        return None

    @property
    def onnx_model(self) -> Optional[OnnxModel]:
        """Quick access to onnx model from interface"""
        return self.interface.onnx_model

    @property
    def model_metadata(self) -> ModelMetadata:
        """Loads `ModelMetadata` class"""

        from opsml.storage.card_loader import ModelCardLoader

        return ModelCardLoader(self).load_model_metadata()

    @property
    def drift_profile(self) -> Optional[Union[SpcDriftProfile]]:
        """Loads drift profile from scouter server"""

        return self.interface.drift_profile

    def load_drift_profile(self) -> Optional[Union[SpcDriftProfile]]:
        """Loads drift profile from model registry"""

        from opsml.storage.card_loader import ModelCardLoader

        ModelCardLoader(self).load_drift_profile()

        return self.drift_profile

    @property
    def card_type(self) -> str:
        return CardType.MODELCARD.value
