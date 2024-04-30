# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import ConfigDict, SerializeAsAny, field_validator

from opsml.cards.base import ArtifactCard
from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.base import ModelInterface
from opsml.types import CardType, ModelCardMetadata, ModelMetadata, OnnxModel

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
                additional kwargs to pass
        """
        # load modelcard loader
        from opsml.storage.card_loader import ModelCardLoader

        ModelCardLoader(self).load_model(load_preprocessor, **kwargs)

    def download_model(
        self,
        path: Path,
        load_preprocessor: bool = False,
        load_onnx: bool = False,
        quantize: bool = False,
        **kwargs: Any,
    ) -> None:
        """Downloads model, preprocessor and metadata to path

        Args:
            path:
                Path to download model
            load_preprocessor:
                Whether to load preprocessor or not. Default is False
            load_onnx:
                Whether to load onnx model or not. Default is False
            quantize:
                Whether to quantize onnx model or not. Default is False

            **kwargs:
                additional kwargs to pass
        """

        from opsml.storage.card_loader import ModelCardLoader

        # set path to download model
        kwargs["lpath"] = path
        kwargs["load_preprocessor"] = load_preprocessor
        kwargs["load_onnx"] = load_onnx
        kwargs["quantize"] = quantize

        ModelCardLoader(self).download_model(**kwargs)

    def load_onnx_model(self, load_preprocessor: bool = False, **kwargs: Any) -> None:
        """Loads onnx model to interface

        Args:
            load_preprocessor:
                Whether to load preprocessor or not. Default is False

            **kwargs:
                Additional kwargs to pass

        """

        from opsml.storage.card_loader import ModelCardLoader

        ModelCardLoader(self).load_onnx_model(load_preprocessor, **kwargs)

    def load_preprocessor(self, **kwargs: Any) -> None:
        """Loads onnx model to interface"""

        if self.preprocessor is not None:
            return

        from opsml.storage.card_loader import ModelCardLoader

        ModelCardLoader(self).load_preprocessor(**kwargs)

    def create_registry_record(self) -> Dict[str, Any]:
        """Creates a registry record from the current ModelCard"""

        exclude_vars = {"interface": {"model", "preprocessor", "sample_data", "onnx_model"}}
        dumped_model = self.model_dump(exclude=exclude_vars)

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
    def card_type(self) -> str:
        return CardType.MODELCARD.value
