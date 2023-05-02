# pylint: disable=import-outside-toplevel
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type, cast, Union
from pydantic.types import ConstrainedList
from functools import cached_property
import numpy as np
from pydantic import create_model, conlist

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
    PydanticDataTypes,
    ApiDataSchemas,
)

PydanticFields = Dict[str, Tuple[Any, ...]]
PredictFunc = Callable[[Dict[str, Any]], Any]


class PydanticFeatureGenerator:
    def __init__(
        self,
        features: Dict[str, Feature],
        model_type: str,
    ):
        """
        Generates pydanitc field for api cretion

        Args:
            features:
                Dictionary of `Feature`

        """

        self.features = features
        self.model_type = model_type
        self.pydantic_fields: PydanticFields = {}

    def _is_list_type(self, feature: Feature) -> bool:

        """
        Checks if feature is a list type

        Args:
            feature:
                `Feature`

        Returns
            boolean
        """
        if feature.feature_type == "UNDEFINED":
            return True

        # it is assumed pytorch/tensorflow will be feeding list/arrays
        if self.model_type in [OnnxModelType.TF_KERAS, OnnxModelType.PYTORCH]:
            return True

        if len(feature.shape) > 1 and feature.shape[1] > 1:
            return True

        return False

    def _get_feature_shape(self, feature: Feature) -> Optional[Union[List[int], int]]:
        """
        Gets feature shape

        Args:
            feature:
                `Feature`

        Returns
            Optional list of ints or int

        """
        feature_len = len(feature.shape)
        if feature_len > 1:
            if feature_len > 2:
                return feature.shape[1:]
            return None if feature.shape[1] == 0 else feature.shape[1]
        return None

    def _get_list_feature_type(self, feature: Feature) -> List[Any]:
        """Creates list feature type to be used with pydantic model.

        Args:
            feature:
                `Feature`

        Returns:
            _type_: _description_
        """
        feature_shape = self._get_feature_shape(feature=feature)
        feature_type = ApiSigTypes[feature.feature_type].value

        if isinstance(feature_shape, list):
            shape_len = len(feature_shape)
        else:
            shape_len = 1
        for _ in range(shape_len):
            feature_type = conlist(feature_type)  # type: ignore

        return feature_type

    def _get_field_from_feature(self, feature: Feature) -> Union[List[Any], str, int, float]:
        """Infer field type and shape from feature"""
        if self._is_list_type(feature=feature):
            return self._get_list_feature_type(feature=feature)
        return ApiSigTypes[feature.feature_type].value

    def get_pydantic_fields(self) -> PydanticFields:
        """Iterate through provided fields and create pydantic field for `create_model`"""
        for input_name, feature in self.features.items():
            field_info = self._get_field_from_feature(feature=feature)
            self.pydantic_fields[input_name] = (field_info, ...)

        return self.pydantic_fields


class ApiSigCreator:
    def __init__(self, data_schema: ApiDataSchemas, model_type: str, to_onnx: bool):
        """
        Creates an API signature from model metadata

        Arga:
            data_dict:
                Data dict of data_type, input features, and outputs from model
            model_type:
                Type of model
            data_schema:
                Schema from sample input data
            to_onnx:
                Whether the api sig is being generated for an onnx model. This is needed for the
                return sig

        """

        self.data_schema = data_schema
        self.model_type = model_type
        self.to_onnx = to_onnx

    @property
    def input_features(self) -> Dict[str, Feature]:
        return self.data_schema.model_data_schema.input_features

    @property
    def output_features(self) -> Dict[str, Feature]:
        return self.data_schema.model_data_schema.output_features

    @cached_property
    def input_sig(self) -> Base:
        input_sig = self._get_input_sig(features=self.input_features)
        input_sig.feature_map = self.input_features  # need for conversions

        return input_sig

    @cached_property
    def output_sig(self) -> Base:

        output_sig = self._get_output_sig(features=self.output_features)
        output_sig.feature_map = self.output_features  # need for conversions

        return output_sig

    def _get_pydantic_sig(self, features: Dict[str, Feature]) -> PydanticFields:
        """
        Infers the pydantic model needed for API signature

        If model was trained on dataframe and expects to supply
        values as prediction to API, _infer_pydantic_fields will be
        called to infer features and types.

        If model was trained on Numpy array and expects to supply
        array/list to API, _infer_pydantic_list will be called, which
        will create a pydantic model that expects a list of feaure size.

        Returns
            PydanticFields model to be used with FastAPI
        """

        pydantic_generator = PydanticFeatureGenerator(features=features, model_type=self.model_type)
        return pydantic_generator.get_pydantic_fields()

    def _get_pydantic_base(self):
        raise NotImplementedError

    def _get_base_fields(self, features: Dict[str, Feature]) -> Tuple[Base, PydanticFields]:
        pydantic_fields = self._get_pydantic_sig(features=features)
        base = self._get_pydantic_base()

        return base, pydantic_fields

    def _get_input_sig(self, features: Dict[str, Feature]) -> Type[Base]:
        base, fields = self._get_base_fields(features=features)
        input_sig = create_model("Features", **fields, __base__=base)  # type: ignore
        return input_sig

    def _convert_to_conlist(self, field_value: Tuple[Any, Ellipsis]) -> Tuple[ConstrainedList, Ellipsis]:
        if issubclass(field_value[0], ConstrainedList):
            return field_value
        return (conlist(field_value[0]), ...)

    def _get_output_sig(self, features: Dict[str, Feature]) -> Type[Base]:
        base, fields = self._get_base_fields(features=features)

        if not self.to_onnx:
            return create_model("Predictions", **fields, __base__=base)

        # Onnx assumes array output
        for field_name, field_value in fields.items():
            field = self._convert_to_conlist(field_value=field_value)
            fields[field_name] = field

        return create_model("Predictions", **fields, __base__=base)

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
    def _get_input_sig(self, features: Dict[str, Feature]) -> Type[Base]:
        if self.data_schema is not None:
            return super()._get_input_sig(features=self.data_schema.input_data_schema)
        return super()._get_input_sig(features=features)

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
        model_type: str,
        to_onnx: bool,
        data_schema: ApiDataSchemas,
    ):
        creator = next(
            (
                sig_creator
                for sig_creator in ApiSigCreator.__subclasses__()
                if sig_creator.validate_model_type(model_type=model_type)
            )
        )

        return creator(
            model_type=model_type,
            data_schema=data_schema,
            to_onnx=to_onnx,
        )
