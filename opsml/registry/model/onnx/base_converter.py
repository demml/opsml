# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict, List, Optional, Tuple, cast

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import OpsmlImportExceptions
from opsml.registry.model.interfaces import ModelInterface
from opsml.registry.model.onnx.data_converters import OnnxDataConverter
from opsml.registry.model.onnx.metadata_creator import _TrainedModelMetadataCreator
from opsml.registry.model.onnx.registry_updaters import OnnxRegistryUpdater
from opsml.registry.model.utils.data_helper import ModelDataHelper, get_model_data
from opsml.registry.types import (
    LIGHTGBM_SUPPORTED_MODEL_TYPES,
    SKLEARN_SUPPORTED_MODEL_TYPES,
    DataSchema,
    Feature,
    ModelReturn,
    OnnxModel,
    TrainedModelType,
)

logger = ArtifactLogger.get_logger()


try:
    import onnx
    import onnxruntime as rt
    from onnx import ModelProto

except ModuleNotFoundError as import_error:
    logger.error(
        """Failed to import onnx and onnxruntime. Please install onnx and onnxruntime via opsml extras
        If you wish to convert your model to onnx"""
    )
    raise import_error


class _ModelConverter:
    def __init__(self, model_interface: ModelInterface, data_helper: ModelDataHelper):
        self._interface = model_interface
        self.data_helper = data_helper
        self._sess: Optional[rt.InferenceSession] = None

    @property
    def interface(self) -> ModelInterface:
        return cast(ModelInterface, self._interface)

    @property
    def sess(self) -> rt.InferenceSession:
        assert self._sess is not None
        return self._sess

    @property
    def model_type(self) -> str:
        return self.interface.model_type

    @property
    def model_class(self) -> str:
        return self.interface.model_class

    @property
    def trained_model(self) -> Any:
        return self.interface.model

    @property
    def onnx_model(self) -> Optional[OnnxModel]:
        return self.interface.onnx_model

    @property
    def is_sklearn_classifier(self) -> bool:
        """Checks if model is a classifier"""

        from sklearn.base import is_classifier

        return bool(is_classifier(self.trained_model))

    def update_onnx_registries(self) -> bool:
        return OnnxRegistryUpdater.update_onnx_registry(
            model_estimator_name=self.model_type,
        )

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts a model to onnx format

        Returns
            Encrypted model definition
        """
        raise NotImplementedError

    def get_data_types(self) -> Tuple[List[Any], Optional[Dict[str, Feature]]]:
        """Converts data for onnx

        Returns
            Encrypted model definition
        """
        if self.model_type in [*SKLEARN_SUPPORTED_MODEL_TYPES, *LIGHTGBM_SUPPORTED_MODEL_TYPES]:
            OpsmlImportExceptions.try_skl2onnx_imports()
        elif self.model_type == TrainedModelType.TF_KERAS:
            OpsmlImportExceptions.try_tf2onnx_imports()
        return OnnxDataConverter(model_interface=self.interface, data_helper=self.data_helper).get_data_types()

    def _get_data_elem_type(self, sig: Any) -> int:
        return int(sig.type.tensor_type.elem_type)

    @classmethod
    def _parse_onnx_signature(cls, sess: rt.InferenceSession, sig_type: str) -> Dict[str, Feature]:  # type: ignore[type-arg]
        feature_dict = {}
        assert sess is not None

        signature: List[Any] = getattr(sess, f"get_{sig_type}")()

        for sig in signature:
            feature_dict[sig.name] = Feature(feature_type=sig.type, shape=tuple(sig.shape))

        return feature_dict

    @classmethod
    def create_feature_dict(cls, sess: rt.InferenceSession) -> Tuple[Dict[str, Feature], Dict[str, Feature]]:
        """Creates feature dictionary from onnx model

        Args:
            onnx_model:
                Onnx model
        Returns:
            Tuple of input and output feature dictionaries
        """

        input_dict = cls._parse_onnx_signature(sess, "inputs")
        output_dict = cls._parse_onnx_signature(sess, "outputs")

        return input_dict, output_dict

    def create_onnx_model_def(self) -> OnnxModel:
        """Creates Model definition

        Args:
            onnx_model:
                Onnx model
        """

        return OnnxModel(
            onnx_version=onnx.__version__,  # type: ignore
            sess=self.sess,
        )

    def _create_onnx_model(self, initial_types: List[Any]) -> Tuple[OnnxModel, Dict[str, Feature], Dict[str, Feature]]:
        """Creates onnx model, validates it, and creates an onnx feature dictionary

        Args:
            initial_types:
                Initial types for onnx model

        Returns:
            Tuple containing onnx model, input features, and output features
        """

        onnx_model = self.convert_model(initial_types=initial_types)
        self._create_onnx_session(onnx_model=onnx_model)

        # onnx sess can be used to get name, type, shape
        input_onnx_features, output_onnx_features = self.create_feature_dict(sess=self.sess)
        model_def = self.create_onnx_model_def()

        return model_def, input_onnx_features, output_onnx_features

    def _load_onnx_model(self) -> Tuple[OnnxModel, Dict[str, Feature], Dict[str, Feature]]:
        """
        Loads onnx model from model definition

        Returns:
            Tuple containing onnx model definition, input features, and output features
        """
        assert isinstance(self.onnx_model, OnnxModel)
        onnx_model = onnx.load_from_string(self.onnx_model.model_bytes)
        input_onnx_features, output_onnx_features = self.create_feature_dict(onnx_model=onnx_model)

        return self.onnx_model, input_onnx_features, output_onnx_features

    def convert(self) -> ModelReturn:
        """Converts model to onnx model, validates it, and creates an
        onnx feature dictionary

        Returns:
            ModelReturn object containing model definition and api data schema
        """
        initial_types = self.get_data_types()

        if self.onnx_model is None:
            onnx_model, onnx_input_features, onnx_output_features = self._create_onnx_model(initial_types)

        else:
            onnx_model, onnx_input_features, onnx_output_features = self._load_onnx_model()

        schema = DataSchema(
            onnx_input_features=onnx_input_features,
            onnx_output_features=onnx_output_features,
            onnx_version=onnx.__version__,
        )

        return ModelReturn(onnx_model=onnx_model, data_schema=schema)

    def _create_onnx_session(self, onnx_model: ModelProto) -> None:
        self._sess = rt.InferenceSession(
            path_or_bytes=onnx_model.SerializeToString(),
            providers=rt.get_available_providers(),  # failure when not setting default providers as of rt 1.16
        )

    @staticmethod
    def validate(model_class: str) -> bool:
        """validates model base class"""
        raise NotImplementedError


class _OnnxConverterHelper:
    @staticmethod
    def convert_model(model_interface: ModelInterface, data_helper: ModelDataHelper) -> ModelReturn:
        """
        Instantiates a helper class to convert machine learning models and their input
        data to onnx format for interoperability.


        Args:
            model_interface:
                ModelInterface class containing model-specific information for Onnx conversion
            data_helper:
                ModelDataHelper class containing model-specific information for Onnx conversion

        """

        converter = next(
            (
                converter
                for converter in _ModelConverter.__subclasses__()
                if converter.validate(model_class=model_interface.model_class)
            )
        )

        return converter(
            model_interface=model_interface,
            data_helper=data_helper,
        ).convert()


class _OnnxModelConverter(_TrainedModelMetadataCreator):
    def __init__(self, model_interface: ModelInterface):
        """
        Instantiates OnnxModelCreator that is used for converting models to Onnx

        Args:
            model_interface:
                ModelInterface class containing model-specific information for Onnx conversion
        """

        super().__init__(model_interface=model_interface)

    def convert_model(self) -> ModelReturn:
        """
        Create model card from current model and sample data

        Returns
            `ModelReturn`
        """

        model_data = get_model_data(
            data_type=self.interface.data_type,
            input_data=self.interface.sample_data,
        )

        onnx_model_return = _OnnxConverterHelper.convert_model(model_interface=self.interface, data_helper=model_data)

        # set extras
        onnx_model_return.data_schema.input_features = self._get_input_schema()
        onnx_model_return.data_schema.output_features = self._get_output_schema()
        onnx_model_return.data_schema.data_type = self.interface.data_type

        # add onnx version
        return onnx_model_return

    #
    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if to_onnx:
            return True
        return False


def _get_onnx_metadata(model_interface: ModelInterface, onnx_model: rt.InferenceSession) -> ModelReturn:
    """Helper for extracting model metadata for a model that is skipping auto onnx conversion.
    This is primarily used for huggingface models.

    Args:
        model_interface:
            ModelInterface
        onnx_model:
            Onnx inference session
    """
    # set metadata
    meta_creator = _TrainedModelMetadataCreator(model_interface)
    metadata = meta_creator.get_model_metadata()

    onnx_input_features, onnx_output_features = _ModelConverter.create_feature_dict(
        cast(rt.InferenceSession, onnx_model.model),
    )

    metadata.data_schema.onnx_input_features = onnx_input_features
    metadata.data_schema.onnx_output_features = onnx_output_features

    return metadata
