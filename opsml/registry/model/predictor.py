# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from typing import Any, Dict

from opsml.registry.types import ApiDataSchemas


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

        self.sig_creator = None  # TODO: revamp onnx

    @property
    def data_type(self) -> str:
        return str(self.data_schema.model_data_schema.data_type)

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

        pass
