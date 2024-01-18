# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# mypy: disable-error-code="arg-type"

import json
from pathlib import Path
from typing import Any

from opsml.model import HuggingFaceModel, ModelInterface
from opsml.types import ModelMetadata, OnnxModel, SaveName, Suffix


class ModelLoader:
    """Helper class for loading models from disk and downloading via opsml-cli"""

    def __init__(self, path: Path):
        """Initialize ModelLoader

        Args:
            interface:
                ModelInterface for the model
            path:
                Directory path to the model artifacts
        """

        self.path = path
        self.metadata = self._load_metadata()
        self.interface = self._load_interface()

    def _load_interface(self) -> ModelInterface:
        """Loads a ModelInterface from disk using metadata

        Args:
            interface:
                ModelInterface to load

        Returns:
            ModelInterface
        """
        from opsml.storage.card_loader import _get_model_interface

        Interface = _get_model_interface(self.metadata.model_interface)  # pylint: disable=invalid-name

        loaded_interface = Interface.model_construct(
            _fields_set={"name", "repository", "version"},
            **{
                "name": self.metadata.model_name,
                "repository": self.metadata.model_repository,
                "version": self.metadata.model_version,
            },
        )

        loaded_interface.model_type = self.metadata.model_type

        if hasattr(self.metadata, "prepocessor_name"):
            loaded_interface.preprocessor_name = self.metadata.preprocessor_name

        if hasattr(self.metadata, "tokenizer_name"):
            loaded_interface.tokenizer_name = self.metadata.tokenizer_name

        if hasattr(self.metadata, "feature_extractor_name"):
            loaded_interface.feature_extractor_name = self.metadata.feature_extractor_name

        return loaded_interface

    @property
    def model(self) -> Any:
        return self.interface.model

    @property
    def onnx_model(self) -> OnnxModel:
        assert self.interface.onnx_model is not None, "OnnxModel not loaded"
        return self.interface.onnx_model

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

    def _load_metadata(self) -> ModelMetadata:
        """Load metadata from disk"""
        metadata_path = (self.path / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)

        with metadata_path.open("r") as file_:
            return ModelMetadata(**json.load(file_))

    def _load_huggingface_preprocessors(self) -> None:
        """Load huggingface preprocessors from disk"""

        assert isinstance(self.interface, HuggingFaceModel), "HuggingFaceModel interface required"

        if self.preprocessor is not None:
            return

        if hasattr(self.metadata, "tokenizer_name"):
            load_path = (self.path / SaveName.TOKENIZER.value).with_suffix("")
            self.interface.load_tokenizer(load_path)
            return

        if hasattr(self.metadata, "feature_extractor_name"):
            load_path = (self.path / SaveName.FEATURE_EXTRACTOR.value).with_suffix("")
            self.interface.load_feature_extractor(load_path)
            return

        return

    def load_preprocessor(self) -> None:
        """Load preprocessor from disk"""

        if isinstance(self.interface, HuggingFaceModel):
            self._load_huggingface_preprocessors()
            return

        if hasattr(self.metadata, "preprocessor_name"):
            load_path = (self.path / SaveName.PREPROCESSOR.value).with_suffix(self.interface.preprocessor_suffix)
            self.interface.load_preprocessor(load_path)
            return

        return

    def load_model(self, **kwargs: Any) -> None:
        load_path = (self.path / SaveName.TRAINED_MODEL.value).with_suffix(self.interface.model_suffix)
        self.interface.load_model(load_path, **kwargs)

        if isinstance(self.interface, HuggingFaceModel):
            if self.interface.is_pipeline:
                self.interface.to_pipeline()

    def _load_huggingface_onnx_model(self, **kwargs: Any) -> None:
        assert isinstance(self.interface, HuggingFaceModel), "Expected HuggingFaceModel"
        load_quantized = kwargs.get("load_quantized", False)
        save_name = SaveName.QUANTIZED_MODEL.value if load_quantized else SaveName.ONNX_MODEL.value

        if self.interface.is_pipeline:
            self._load_huggingface_preprocessors()

        load_path = (self.path / save_name).with_suffix(self.interface.model_suffix)
        self.interface.onnx_model = OnnxModel(onnx_version=self.metadata.onnx_version)
        self.interface.load_onnx_model(load_path)

    def load_onnx_model(self, **kwargs: Any) -> None:
        """Load onnx model from disk

        Kwargs:

            ------Note: These kwargs only apply to HuggingFace models------

            kwargs:
                load_quantized:
                    If True, load quantized model

                onnx_args:
                    Additional onnx args needed to load the model

        """
        if isinstance(self.interface, HuggingFaceModel):
            self.interface.onnx_args = kwargs.get("onnx_args", None)
            self._load_huggingface_onnx_model(**kwargs)
            return

        load_path = (self.path / SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value)
        self.interface.onnx_model = OnnxModel(onnx_version=self.metadata.onnx_version)
        self.interface.load_onnx_model(load_path)
        return
