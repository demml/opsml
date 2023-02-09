# pylint: disable=import-outside-toplevel
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type

import numpy as np
from pydantic import create_model

from opsml_artifacts.registry.model.types import (
    ApiSigTypes,
    Base,
    DataDict,
    DeepLearningDictBase,
    DeepLearningNumpyBase,
    DictBase,
    Feature,
    InputDataType,
    NumpyBase,
    OnnxModelType,
)

PydanticFields = Dict[str, Tuple[Any, ...]]
PredictFunc = Callable[[Dict[str, Any]], Any]


class ApiSigCreator:
    def __init__(
        self,
        data_type: str,
        data_dict: DataDict,
        model_type: str,
        data_schema: Optional[Dict[str, Feature]],
    ):
        self.data_schema = data_schema
        self.data_type = data_type
        self.model_type = model_type
        self.data_dict = data_dict

    def _is_list_type(self, feature: Feature):
        if feature.feature_type == "UNDEFINED":
            return True
        if self.model_type in [OnnxModelType.TF_KERAS, OnnxModelType.PYTORCH]:
            return True
        if len(feature.shape) > 1 and feature.shape[1] > 1:
            return True
        return False

    def _get_feature_shape(self, feature: Feature):
        feature_len = len(feature.shape)
        if feature_len > 1:
            if feature_len > 2:
                return feature.shape[1:]
            return None if feature.shape[1] == 0 else feature.shape[1]
        return None

    def _infer_pydantic_fields(self, features: Dict[str, Feature]) -> PydanticFields:
        pydantic_fields: PydanticFields = {}

        for input_name, feature in features.items():
            if self._is_list_type(feature=feature):
                feature_shape = self._get_feature_shape(feature=feature)
                field_info = ApiSigTypes[feature.feature_type].value

                if isinstance(feature_shape, list):
                    shape_len = len(feature_shape)
                else:
                    shape_len = 1
                for _ in range(shape_len):
                    field_info = List[field_info]  # type: ignore

            else:
                field_info = ApiSigTypes[feature.feature_type].value
            pydantic_fields[input_name] = (field_info, ...)

        return pydantic_fields

    def _get_pydantic_sig(self, features: Dict[str, Any]) -> PydanticFields:
        """Infers the pydantic model needed for API signature

        If model was trained on dataframe and expects to supply
        values as prediction to API, _infer_pydantic_fields will be
        called to infer features and types.

        If model was trained on Numpy array and expects to supply
        array/list to API, _infer_pydantic_list will be called, which
        will create a pydantic model that expects a list of feaure size.

        Returns
            PydanticFields model to be used with FastAPI
        """

        return self._infer_pydantic_fields(features=features)

    def _get_pydantic_base(self):
        raise NotImplementedError

    def _create_api_sig(self, features: Dict[str, Any]):

        pydantic_fields = self._get_pydantic_sig(features=features)
        base = self._get_pydantic_base()

        feature_sig = create_model("Features", **pydantic_fields, __base__=base)  # type: ignore
        return feature_sig

    def get_api_sig(self, features: Dict[str, Any]) -> Type[Base]:
        if not TYPE_CHECKING:
            feature_sig = self._create_api_sig(features=features)
        else:
            feature_sig = Base

        return feature_sig

    def _get_input_sig(self) -> Type[Base]:
        return self.get_api_sig(features=self.data_dict.input_features)

    def _get_output_sig(self) -> Type[Base]:
        return self.get_api_sig(features=self.data_dict.output_features)

    def get_input_output_sig(self) -> Tuple[Type[Base], Type[Base]]:
        input_sig = self._get_input_sig()
        output_sig = self._get_output_sig()

        return input_sig, output_sig

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        raise NotImplementedError


class SklearnSigCreator(ApiSigCreator):
    def _get_pydantic_base(self):
        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            if self.data_type == InputDataType.PANDAS_DATAFRAME.name:
                return DictBase  # onnx sklearn pipelines can accept dictionaries
        return NumpyBase

    #
    def _get_input_sig(self) -> Type[Base]:
        if self.data_schema is not None:
            return self.get_api_sig(features=self.data_schema)
        return self.get_api_sig(features=self.data_dict.input_features)

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type not in ["keras", "pytorch"]


class DeepLearningSigCreator(ApiSigCreator):
    def _get_pydantic_base(self):
        if self.data_type == InputDataType.DICT.name:
            return DeepLearningDictBase
        return DeepLearningNumpyBase

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type in ["keras", "pytorch"]


class ApiSigCreatorGetter:
    @staticmethod
    def get_sig_creator(
        data_type: str,
        data_dict: DataDict,
        model_type: str,
        data_schema: Optional[Dict[str, Feature]],
    ):

        creator = next(
            (
                sig_creator
                for sig_creator in ApiSigCreator.__subclasses__()
                if sig_creator.validate_model_type(model_type=model_type)
            )
        )

        return creator(
            data_type=data_type,
            data_dict=data_dict,
            model_type=model_type,
            data_schema=data_schema,
        )


# need to build response object for prediction
class OnnxModelPredictor:
    def __init__(
        self,
        model_type: str,
        model_definition: bytes,
        data_dict: DataDict,
        data_schema: Optional[Dict[str, Feature]],
        model_version: int,
    ):

        """Instantiates predictor class from ModelCard.

        Args:
            predictor_args (PredictorArgs) Args for predictor creation
        """

        self.model_type = model_type
        self.data_dict = data_dict
        self.data_schema = data_schema
        self.model_version = model_version

        # methods
        self.sess = self._create_onnx_session(model_definition=model_definition)
        self._output_names = [output.name for output in self.sess.get_outputs()]

        api_sig_creator = ApiSigCreatorGetter.get_sig_creator(
            data_type=data_dict.data_type,
            model_type=model_type,
            data_schema=data_schema,
            data_dict=data_dict,
        )
        self.input_sig, self.output_sig = api_sig_creator.get_input_output_sig()

    def predict(self, data: Dict[str, Any]) -> Any:

        """Run prediction on onnx model. Data is expected to conform to pydantic
        schema as defined in "api_sig" attribute. This schema will be used when
        deploying the model api.

        Args:
            Data (dictionary): Record of data as dictionary that conforms to pydantic
            schema.

        Returns:
            Prediction (array or float depending on model type)
        """

        pred_data = self.input_sig(**data)

        predictions = self.sess.run(
            output_names=self._output_names,
            input_feed=pred_data.to_onnx(),
        )

        return predictions

    def predict_with_model(self, model: Any, data: Dict[str, Any]) -> Any:
        """Will test prediction against model by sending data through
        pydantic model.

        Args:
            model (Any sklearn flavor model): Model to send predictions to
            data (dictionary of data): Dictionary containing data for prediction

        Returns
            Predicition (float)
        """

        pred_data = self.input_sig(**data)

        if self.model_type == "sklearn_pipeline":
            new_data = pred_data.to_dataframe()

        elif self.model_type == "keras":
            new_data = pred_data.to_onnx()

        elif self.model_type == "pytorch":
            import torch

            feed_data: Dict[str, np.ndarray] = pred_data.to_onnx()
            new_data = (torch.from_numpy(value) for value in feed_data.values())  # pylint: disable=no-member
            return model(*new_data)

        else:
            new_data = list(pred_data.to_onnx().values())[0]

        prediction = model.predict(new_data)

        return prediction

    def _create_onnx_session(self, model_definition: bytes):
        import onnxruntime as rt  # pylint: disable=import-outside-toplevel

        return rt.InferenceSession(model_definition)
