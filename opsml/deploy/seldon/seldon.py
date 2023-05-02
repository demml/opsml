from typing import Union, Dict, Any
from opsml.helpers.logging import ArtifactLogger
from opsml.model.types import Feature, SeldonSigTypes
from opsml.deploy.loader import ModelLoader

logger = ArtifactLogger.get_logger(__name__)


class SeldonModel:
    def __init__(self):
        """Class for loading a model in from a ModelDefinition and deploying it through Seldon"""
        self.model = ModelLoader().load_models()[0]
        self.model.start_onnx_session()

    def _get_sig_metadata(
        self,
        features: Dict[str, Any],
        feature_map: Dict[str, Feature],
    ):
        sig_meta = []

        for feature in features:
            feature_info = feature_map[feature]
            sig_meta.append(
                {
                    "datatype": SeldonSigTypes[feature_info.feature_type].value,
                    "name": feature,
                    "shape": feature_info.shape[1:],
                },
            )

        return sig_meta

    def init_metadata(self):
        """Creates metadata for loaded model"""

        inputs = self._get_sig_metadata(
            features=self.model.input_sig.schema().get("properties"),
            feature_map=self.model.input_sig.feature_map,
        )

        outputs = self._get_sig_metadata(
            features=self.model.output_sig.schema().get("properties"),
            feature_map=self.model.output_sig.feature_map,
        )

        meta = {
            "name": self.model.name,
            "platform": "seldon",
            "versions": [self.model.version],
            "inputs": inputs,
            "outputs": outputs,
        }

        return meta

    def predict_raw(self, request):
        """
        Takes raw payload, validates it and makes a prediction.
        Steps:
            (1) Request is passed to dynamic pydantic model built from input features
            (2) pydantic-validated payload is passed to model class for prediction
            (3) prediction is passed to outgoing pydantic model for validation

        """

        payload = self.model.input_sig(**request)
        preds = self.model.predict(payload=payload)
        output = self.model.output_sig(**preds)

        return output.dict()

    def tags(self):
        return {
            "name": self.model.name,
            "version": self.model.version,
        }
