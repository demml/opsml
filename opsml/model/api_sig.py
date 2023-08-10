# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from functools import cached_property
from typing import Any, Callable, Dict, List, Tuple, Union

from pydantic import conlist, create_model

from opsml.model.types import (
    ApiDataSchemas,
    ApiSigTypes,
    Base,
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


class PydanticFeatureGenerator:
    def __init__(
        self,
        features: Dict[str, Feature],
        model_type: str,
    ):
        """
        Generates pydantic field for api creation

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

        if len(feature.shape) > 2:
            return True

        return False

    def _get_feature_shape(self, feature: Feature) -> List[int]:
        """
        Gets feature shape

        Args:
            feature:
                `Feature`

        Returns
            Optional list of ints or int

        """

        feature_len = len(feature.shape)
        if feature_len > 2:
            return feature.shape[1:]
        return [1] if feature.shape[1] == 0 else [feature.shape[1]]

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

        shape_len = len(feature_shape)
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

        Args:
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

    @property
    def data_type(self) -> str:
        data_type = self.data_schema.model_data_schema.data_type
        if data_type is not None:
            return data_type
        raise ValueError("Data type not passed to api sig creator")

    @cached_property
    def input_sig(self) -> Base:
        input_sig = self._get_input_sig(features=self.input_features)
        input_sig.feature_map = self.input_features  # type: ignore
        return input_sig

    @cached_property
    def output_sig(self) -> Base:
        output_sig = self._get_output_sig(features=self.output_features)
        output_sig.feature_map = self.output_features  # type: ignore
        return output_sig

    def _get_pydantic_sig(self, features: Dict[str, Feature]) -> PydanticFields:
        """
        Infers the pydantic model needed for API signature

        Args:
            features:
                Dictionary of keys and `Feature` objects

        Returns
            PydanticFields model to be used with an API
        """

        pydantic_generator = PydanticFeatureGenerator(features=features, model_type=self.model_type)
        return pydantic_generator.get_pydantic_fields()

    def _get_pydantic_base(self):
        raise NotImplementedError

    def _get_base_fields(self, features: Dict[str, Feature]) -> Tuple[Base, PydanticFields]:
        """
        Creates fields and `Base` for api signature

        Args:
            features:
                Dictionary of keys and `Feature` objects

        Returns:
            `Base` and `PydanticFields`
        """
        pydantic_fields = self._get_pydantic_sig(features=features)
        base = self._get_pydantic_base()

        return base, pydantic_fields

    def _get_input_sig(self, features: Dict[str, Feature]) -> Base:
        """
        Creates input sig for a model

        Args:
            features:
                Dictionary of keys and `Feature` objects

        Returns:
            Pydantic `Base`

        """
        base, fields = self._get_base_fields(features=features)
        return create_model("Features", **fields, __base__=base)  # type: ignore

    def _get_output_sig(self, features: Dict[str, Feature]) -> Base:
        """
        Creates output sig for a model. Uses an Any type in order to support multiple output formats

        Args:
            features:
                Dictionary of keys and `Feature` objects

        Returns:
            Pydantic `Base`

        """
        pydantic_fields = {}
        base = self._get_pydantic_base()

        for feature in features.keys():
            pydantic_fields[feature] = (Any, ...)

        return create_model("Predictions", **pydantic_fields, __base__=base)  # type: ignore

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        raise NotImplementedError


class SklearnSigCreator(ApiSigCreator):
    def _get_pydantic_base(self):
        """
        Gets pydantic base for sklearn model that depends on type. Onnx accepts dictionary inputs for pipeline
        models
        """
        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            if self.data_type == InputDataType.PANDAS_DATAFRAME.name:
                return DictBase  # onnx sklearn pipelines can accept dictionaries
        return NumpyBase

    #
    def _get_input_sig(self, features: Dict[str, Feature]) -> Base:
        """
        Generates an input sig for an sklearn model. Onnx mainly supports arrays as input; however,
        there are times where we'd like to supply a dict to an api instead of an array for feature mapping.
        If a data schema (dict of features, determined by sample training data) is detected, this method will change
        the input sig to accept a dictionary as input.

        Args:
            features:
                Dictionary of keys and `Feature` objects

        Returns:
            Pydantic `Base`
        """
        if self.data_schema.input_data_schema is not None:
            return super()._get_input_sig(features=self.data_schema.input_data_schema)
        return super()._get_input_sig(features=features)

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type not in [
            OnnxModelType.TF_KERAS,
            OnnxModelType.PYTORCH,
            OnnxModelType.TRANSFORMER,
        ]


class DeepLearningSigCreator(ApiSigCreator):
    def _get_pydantic_base(self):
        """Gets pydantic base for deep learning models"""
        if self.data_type == InputDataType.DICT.name:
            return DeepLearningDictBase
        return DeepLearningNumpyBase

    @staticmethod
    def validate_model_type(model_type: str) -> bool:
        return model_type in [
            OnnxModelType.TF_KERAS,
            OnnxModelType.PYTORCH,
            OnnxModelType.TRANSFORMER,
        ]


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
