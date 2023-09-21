# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from functools import cached_property
from typing import Any, Dict, List

import numpy as np

from opsml.model.api_sig import ApiSigCreatorGetter
from opsml.model.types import ApiDataSchemas, Base, InputDataType, OnnxModelType


# need to build response object for prediction
class OnnxModelPredictor:
    def __init__(
        self,
        model_name: str,
        model_type: str,
        model_definition: bytes,
        onnx_version: str,
        data_schema: ApiDataSchemas,
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
        self.data_schema = data_schema
        self.model_version = model_version
        self.model_definition = model_definition
        self.onnx_version = onnx_version
        self.sample_api_data = sample_api_data

        # placeholder for eventual trained model predictor expansion
        self.to_onnx = True

        # methods
        if start_sess:
            self.sess = self._create_onnx_session(model_definition=model_definition)
            self._output_names = [output.name for output in self.sess.get_outputs()]

        self.sig_creator = ApiSigCreatorGetter.get_sig_creator(
            model_type=model_type,
            data_schema=self.data_schema,
            to_onnx=self.to_onnx,
        )

    @property
    def data_type(self):
        return self.data_schema.model_data_schema.data_type

    @cached_property
    def input_sig(self) -> Base:
        return self.sig_creator.input_sig

    @cached_property
    def output_sig(self) -> Base:
        return self.sig_creator.output_sig

    def predict(self, data: Dict[str, Any]) -> Any:
        """
        Run prediction on onnx model. Data is expected to conform to pydantic
        schema as defined in "api_sig" attribute. This schema will be used when
        deploying the model api.

        Args:
            data:
                Record of data as dictionary that conforms to pydantic schema.

        Returns:
            Prediction (array or float depending on model type)
        """

        pred_data = self.sig_creator.input_sig(**data)
        prediction = self.sess.run(
            output_names=self._output_names,
            input_feed=pred_data.to_onnx(),
        )
        return self._extract_predictions(prediction=prediction)

    def _extract_predictions(self, prediction: List[Any]) -> Dict[str, Any]:
        """Parses onnx runtime prediction

        Args:
            Predictions:
                Onnx runtime prediction list

        Returns:
            Prediction in the form of a key value mapping
        """
        output_dict = {}

        for idx, output in enumerate(self._output_names):
            if output == "variable":
                output = "value"

            pred = prediction[idx]

            if isinstance(pred, np.ndarray):
                output_dict[output] = pred.tolist()

            else:
                output_dict[output] = pred

        return output_dict

    def predict_with_model(self, model: Any, data: Dict[str, Any]) -> Any:
        """Will test prediction against model by sending data through
        pydantic model.

        Args:
            model : Model to send predictions to
            data (dictionary of data): Dictionary containing data for prediction

        Returns
            Prediction (float)
        """

        pred_data = self.sig_creator.input_sig(**data)

        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            data_for_pred = pred_data.to_dataframe()

        elif self.model_type == OnnxModelType.TF_KERAS:
            data_for_pred = pred_data.to_onnx()

        elif self.model_type in [OnnxModelType.PYTORCH, OnnxModelType.TRANSFORMER]:
            import torch

            feed_data: Dict[str, np.ndarray] = pred_data.to_onnx()

            if self.data_type == InputDataType.DICT:
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

        return rt.InferenceSession(
            path_or_bytes=model_definition,
            providers=rt.get_available_providers(),
        )
