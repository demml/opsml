from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Type, cast

from pydantic import conlist, create_model

from opsml_artifacts.registry.model.types import (
    Base,
    DataDict,
    InputDataType,
    NumpyBase,
    OnnxModelType,
    PandasBase,
)

PydanticFields = Dict[str, Tuple[Any, ...]]
PredictFunc = Callable[[Dict[str, Any]], Any]


class ModelApiSigCreator:
    def __init__(
        self,
        data_dict: DataDict,
        model_type: str,
        data_schema: Optional[Dict[str, str]],
    ):
        self.data_schema = data_schema
        self.data_dict = data_dict
        self.model_type = model_type

    def _infer_pydantic_fields(self, data_schema: Dict[str, str]) -> PydanticFields:
        pydantic_fields: PydanticFields = {}
        for feature, feature_type in data_schema.items():
            pydantic_fields[feature] = (feature_type, ...)

        return pydantic_fields

    def _infer_pydantic_list(self) -> PydanticFields:
        pydantic_fields: PydanticFields = {}
        input_name, feature = next(iter(self.data_dict.features.items()))
        pydantic_fields[input_name] = (
            conlist(
                float,
                min_items=feature.shape[1],
                max_items=feature.shape[1],
            ),
            ...,
        )

        return pydantic_fields

    def _get_pydantic_sig(self) -> PydanticFields:
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

        if self.data_schema is None:
            return self._infer_pydantic_list()

        data_schema = cast(Dict[str, str], self.data_schema)
        return self._infer_pydantic_fields(data_schema=data_schema)

    def _create_api_sig(self):
        pydantic_fields = self._get_pydantic_sig()
        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            if self.data_dict.data_type == InputDataType.PANDAS_DATAFRAME.name:
                base = PandasBase  # onnx sklearn pipelines can accept dictionaries
        else:
            base = NumpyBase

        feature_sig = create_model("Features", **pydantic_fields, __base__=base)
        return feature_sig

    def get_input_api_sig(self) -> Type[Base]:
        if not TYPE_CHECKING:
            feature_sig = self._create_api_sig()
        else:
            feature_sig = Base

        return feature_sig


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
        self._label_name = [output.name for output in self.sess.get_outputs()]

        api_sig_creator = ModelApiSigCreator(data_dict=data_dict, model_type=model_type, data_schema=data_schema)
        self.input_sig = api_sig_creator.get_input_api_sig()

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

        prediction = self.sess.run(
            output_names=self._label_name,
            input_feed=pred_data.to_onnx(),
        )

        return float(prediction[0])

    def predict_with_model(self, model: Any, data: Dict[str, Any]) -> float:
        """Will test prediction against model by sending data through
        pydantic model.

        Args:
            model (Any sklearn flavor model): Model to send predictions to
            data (dictionary of data): Dictionary containing data for prediction

        Returns
            Predicition (float)
        """

        pred_data = self.api_sig(**data)

        if self.model_type == "sklearn_pipeline":
            onnx_pred = pred_data.to_dataframe()
        else:
            onnx_pred = pred_data.to_onnx()["inputs"]

        prediction = model.predict(onnx_pred)[0]
        return prediction

    def _create_onnx_session(self, model_definition: bytes):
        import onnxruntime as rt  # pylint: disable=import-outside-toplevel

        return rt.InferenceSession(model_definition)
