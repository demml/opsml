from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.base import ModelInterface
from opsml.model.metadata_creator import _TrainedModelMetadataCreator
from opsml.model.utils.data_helper import ModelDataHelper, get_model_data
from opsml.types import ModelReturn

logger = ArtifactLogger.get_logger()

try:
    import onnx
    import onnxruntime as rt

    from opsml.model.onnx.base_converter import _ModelConverter
    from opsml.model.onnx.lightgbm_converter import _LightGBMBoosterOnnxModel
    from opsml.model.onnx.sklearn_converter import _SklearnOnnxModel
    from opsml.model.onnx.tensorflow_converter import _TensorflowKerasOnnxModel

except ModuleNotFoundError as import_error:
    logger.error(
        """Failed to import onnx and onnxruntime. Please install onnx and onnxruntime via opsml extras
        If you wish to convert your model to onnx"""
    )
    raise import_error


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
    onnx_input_features, onnx_output_features = _ModelConverter.create_feature_dict(onnx_model)

    metadata.data_schema.onnx_input_features = onnx_input_features
    metadata.data_schema.onnx_output_features = onnx_output_features
    metadata.data_schema.onnx_version = onnx.__version__  # type: ignore[attr-defined]

    return metadata
