from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Type, cast

from pydantic import conlist, create_model
import numpy as np
from opsml_artifacts.registry.model.types import (
    Base,
    DataDict,
    InputDataType,
    NumpyBase,
    OnnxModelType,
    # PandasBase,
    ApiBase,
    Feature,
    ApiSigTypes,
)

PydanticFields = Dict[str, Tuple[Any, ...]]
PredictFunc = Callable[[Dict[str, Any]], Any]


class ApiSigCreator:
    def __init__(
        self,
        data_type: str,
        data_dict: DataDict,
        model_type: str,
        data_schema: Optional[Dict[str, str]],
    ):
        self.data_schema = data_schema
        self.data_type = data_type
        self.model_type = model_type
        self.data_dict = data_dict

    def _infer_pydantic_fields(self, features: Dict[str, Feature]) -> PydanticFields:
        pydantic_fields: PydanticFields = {}
        for input_name, feature in features.items():
            if feature.shape[1] > 1:
                field_info = conlist(
                    ApiSigTypes[feature.feature_type].value,
                    min_items=feature.shape[1],
                    max_items=feature.shape[1],
                )
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

    # def _get_pydantic_base(self):
    #
    #    if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
    #        if self.data_type == InputDataType.PANDAS_DATAFRAME.name:
    #            return PandasBase  # onnx sklearn pipelines can accept dictionaries
    #
    #    else:
    #        return NumpyBase
    #
    def _get_pydantic_base(self):
        raise NotImplementedError

    def _create_api_sig(self, features: Dict[str, Any]):

        pydantic_fields = self._get_pydantic_sig(features=features)
        # base = self._get_pydantic_base()

        feature_sig = create_model("Features", **pydantic_fields, __base__=ApiBase)
        return feature_sig

    def get_api_sig(self, features: Dict[str, Any]) -> Type[Base]:
        if not TYPE_CHECKING:
            feature_sig = self._create_api_sig(features=features)
        else:
            feature_sig = Base

        return feature_sig

    def get_input_output_sig(self) -> Tuple[Type[Base], Type[Base]]:
        raise NotImplementedError

    def validate_model_type(model_type: str) -> bool:
        raise NotImplementedError


class SklearnSigCreator(ApiSigCreator):
    # def _get_pydantic_base(self):
    #    if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
    #        if self.data_type == InputDataType.PANDAS_DATAFRAME.name:
    #            return PandasBase  # onnx sklearn pipelines can accept dictionaries
    #    else:
    #        return NumpyBase
    #
    def _get_input_sig(self) -> Type[Base]:
        if self.data_schema is not None:
            return self.get_api_sig(features=self.data_schema)
        else:
            return self.get_api_sig(features=self.data_dict.input_features)

    def _get_output_sig(self) -> Type[Base]:
        return self.get_api_sig(features=self.data_dict.output_features)

    def get_input_output_sig(self) -> Tuple[Type[Base], Type[Base]]:
        input_sig = self._get_input_sig()
        output_sig = self._get_output_sig()

        return output_sig, input_sig

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type != "keras"


class TensorflowSigCreator(ApiSigCreator):
    # def _get_pydantic_base(self):
    #    if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
    #        if self.data_type == InputDataType.PANDAS_DATAFRAME.name:
    #            return PandasBase  # onnx sklearn pipelines can accept dictionaries
    #    else:
    #        return NumpyBase
    #
    def _get_input_sig(self) -> Type[Base]:
        return self.get_api_sig(features=self.data_dict.input_features)

    def _get_output_sig(self) -> Type[Base]:
        return self.get_api_sig(features=self.data_dict.output_features)

    def get_input_output_sig(self) -> Tuple[Type[Base], Type[Base]]:
        input_sig = self._get_input_sig()
        output_sig = self._get_output_sig()

        return output_sig, input_sig

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type == "keras"


class ModelApiSigCreator:
    def __init__(
        self,
        data_type: str,
        model_type: str,
        data_schema: Optional[Dict[str, str]],
    ):
        self.data_schema = data_schema
        self.data_type = data_type
        self.model_type = model_type

    def _infer_pydantic_fields(self, features: Dict[str, Feature]) -> PydanticFields:
        pydantic_fields: PydanticFields = {}
        for input_name, feature in features.items():
            if feature.shape[1] > 1:
                field_info = conlist(
                    ApiSigTypes[feature.feature_type].value,
                    min_items=feature.shape[1],
                    max_items=feature.shape[1],
                )
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

        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            if self.data_type == InputDataType.PANDAS_DATAFRAME.name:
                return PandasBase  # onnx sklearn pipelines can accept dictionaries

        else:
            return NumpyBase

    def _create_api_sig(self, features: Dict[str, Any]):

        pydantic_fields = self._get_pydantic_sig(features=features)
        base = self._get_pydantic_base()

        feature_sig = create_model("Features", **pydantic_fields, __base__=base)
        return feature_sig

    def get_api_sig(self, features: Dict[str, Feature]) -> Type[Base]:
        if not TYPE_CHECKING:
            feature_sig = self._create_api_sig(features=features)
        else:
            feature_sig = Base

        return feature_sig

    def get_input_output_sig(
        self, input_features: Dict[str, Any], output_features: Dict[str, Feature]
    ) -> Tuple[Type[Base], Type[Base]]:
        raise NotImplementedError


# need to build response object for prediction
class OnnxModelPredictor:
    def __init__(
        self,
        model_type: str,
        model_definition: bytes,
        data_dict: DataDict,
        data_schema: Optional[Dict[str, str]],
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

        api_sig_creator = ModelApiSigCreator(
            data_type=data_dict.data_type,
            model_type=model_type,
            data_schema=data_schema,
        )
        self.input_sig = api_sig_creator.get_api_sig(features=self.data_dict.input_features)
        self.output_sig = api_sig_creator.get_api_sig(features=self.data_dict.output_features)

    def predict(self, data: Dict[str, Any]):

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

    def predict_with_model(self, model: Any, data: Dict[str, Any]) -> float:
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
            onnx_pred = pred_data.to_dataframe()
        else:
            onnx_pred = list(pred_data.to_onnx().values())[0]
        prediction = model.predict(onnx_pred)

        return prediction

    def _create_onnx_session(self, model_definition: bytes):
        import onnxruntime as rt  # pylint: disable=import-outside-toplevel

        return rt.InferenceSession(model_definition)
