# pylint: disable=import-outside-toplevel
from typing import Any, Dict, Optional

import numpy as np

from opsml.model.api_sig import ApiSigCreatorGetter
from opsml.model.types import (
    DataDict,
    Feature,
    InputDataType,
    ModelApiDef,
    OnnxModelType,
)


# need to build response object for prediction
class OnnxModelPredictor:
    def __init__(
        self,
        model_name: str,
        model_type: str,
        model_definition: bytes,
        onnx_version: str,
        data_dict: DataDict,
        data_schema: Optional[Dict[str, Feature]],
        model_version: str,
        sample_api_data: Dict[str, Any],
        start_sess: bool = True,
    ):
        """Instantiates predictor class from ModelCard.

        Args:
            predictor_args (PredictorArgs) Args for predictor creation
        """

        self.model_name = model_name
        self.model_type = model_type
        self.data_dict = data_dict
        self.data_schema = data_schema
        self.model_version = model_version
        self.model_definition = model_definition
        self.onnx_version = onnx_version
        self.sample_api_data = sample_api_data

        # methods
        if start_sess:
            self.sess = self._create_onnx_session(model_definition=model_definition)
            self._output_names = [output.name for output in self.sess.get_outputs()]

        api_sig_creator = ApiSigCreatorGetter.get_sig_creator(
            model_type=model_type,
            data_schema=data_schema,
            data_dict=data_dict,
        )
        self.input_sig, self.output_sig = api_sig_creator.get_input_output_sig()

    def get_api_model(self) -> ModelApiDef:
        return ModelApiDef(
            model_name=self.model_name,
            model_type=self.model_type,
            onnx_definition=self.model_definition,
            onnx_version=self.onnx_version,
            model_version=self.model_version,
            data_dict=self.data_dict,
            sample_data=self.sample_api_data,
            data_schema=self.data_schema,
        )

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
            model : Model to send predictions to
            data (dictionary of data): Dictionary containing data for prediction

        Returns
            Predicition (float)
        """

        pred_data = self.input_sig(**data)

        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            data_for_pred = pred_data.to_dataframe()

        elif self.model_type == OnnxModelType.TF_KERAS:
            data_for_pred = pred_data.to_onnx()

        elif self.model_type == OnnxModelType.PYTORCH:
            import torch

            feed_data: Dict[str, np.ndarray] = pred_data.to_onnx()

            if self.data_dict.data_type == InputDataType.DICT:
                data_for_pred = {
                    name: torch.from_numpy(value) for name, value in feed_data.items()  # pylint: disable=no-member
                }
                return model(**data_for_pred)

            data_for_pred = (torch.from_numpy(value) for value in feed_data.values())  # pylint: disable=no-member

            return model(*data_for_pred)

        else:
            data_for_pred = list(pred_data.to_onnx().values())[0]

        prediction = model.predict(data_for_pred)

        return prediction

    def _create_onnx_session(self, model_definition: bytes):
        import onnxruntime as rt  # pylint: disable=import-outside-toplevel

        return rt.InferenceSession(model_definition)
