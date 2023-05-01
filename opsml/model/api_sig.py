# pylint: disable=import-outside-toplevel
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type

import numpy as np
from pydantic import create_model

from opsml.model.types import (
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
        data_dict: DataDict,
        model_type: str,
        data_schema: Optional[Dict[str, Feature]],
    ):
        """
        Creates an API signature from model metadata

        Arga:
            data_type:
                type of data
            data_dict:
                Data dict of data_type, input features, and outputs from model
            model_type:
                Type of model
            data_schema:
                Schema from sample input data

        """
        self.data_schema = data_schema
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

    def _get_feature_type_map(self, features: Dict[str, Feature]):
        """Generates feature map of name and type for input data.
        This is used to convert data to the correct type for onnx.
        """

        feature_map = {}
        for name, feature in features.items():
            feature_map[name] = feature.feature_type
        return feature_map

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

        input_sig.feature_map = self._get_feature_type_map(  # type: ignore
            features=self.data_dict.input_features,
        )
        output_sig.feature_map = self._get_feature_type_map(  # type: ignore
            features=self.data_dict.output_features,
        )

        return input_sig, output_sig

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        raise NotImplementedError


class SklearnSigCreator(ApiSigCreator):
    def _get_pydantic_base(self):
        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            if self.data_dict.data_type == InputDataType.PANDAS_DATAFRAME.name:
                return DictBase  # onnx sklearn pipelines can accept dictionaries
        return NumpyBase

    #
    def _get_input_sig(self) -> Type[Base]:
        if self.data_schema is not None:
            return self.get_api_sig(features=self.data_schema)
        return self.get_api_sig(features=self.data_dict.input_features)

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type not in [OnnxModelType.TF_KERAS, OnnxModelType.PYTORCH]


class DeepLearningSigCreator(ApiSigCreator):
    def _get_pydantic_base(self):
        if self.data_dict.data_type == InputDataType.DICT.name:
            return DeepLearningDictBase
        return DeepLearningNumpyBase

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type in [OnnxModelType.TF_KERAS, OnnxModelType.PYTORCH]


class ApiSigCreatorGetter:
    @staticmethod
    def get_sig_creator(
        data_dict: DataDict,
        model_type: str,
        data_schema: Optional[Dict[str, Feature]] = None,
    ):
        creator = next(
            (
                sig_creator
                for sig_creator in ApiSigCreator.__subclasses__()
                if sig_creator.validate_model_type(model_type=model_type)
            )
        )

        return creator(
            data_dict=data_dict,
            model_type=model_type,
            data_schema=data_schema,
        )
