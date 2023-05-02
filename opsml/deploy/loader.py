import glob
from typing import Any, Dict, List, cast
import onnxruntime as rt
import os
from functools import cached_property
from opsml.model.types import ModelApiDef, Base
from opsml.helpers.logging import ArtifactLogger
from opsml.model.predictor import ApiSigCreatorGetter

logger = ArtifactLogger.get_logger(__name__)


# todo: expand out to handle non-onnx models
class Model:
    def __init__(self, model_path: str):
        """
        Loads a ModelCard schema from JSON path
        Args:
            model_path:
                Path to JSON file
        Returns:
            Instantiated Model to be used with API app
        """
        self.model = ModelApiDef.parse_file(model_path)

        self.sig_creator = ApiSigCreatorGetter.get_sig_creator(
            data_dict=self.model.data_dict,
            model_type=self.model.model_type,
            data_schema=self.model.data_schema,
            to_onnx=self.to_onnx,
        )
        self.sess: rt.InferenceSession = None
        self._output_names: List[str] = []
        self._confirm_model_loaded()

    @cached_property
    def input_sig(self) -> Base:
        return self.sig_creator.input_sig

    @cached_property
    def output_sig(self) -> Base:
        return self.sig_creator.output_sig

    @property
    def to_onnx(self) -> str:
        return True if self.model.onnx_definition is not None else False

    @property
    def version(self) -> str:
        return self.model.model_version

    @property
    def model_type(self) -> str:
        return self.model.model_type

    @property
    def name(self) -> str:
        return self.model.model_name

    def start_onnx_session(self):
        self.sess = cast(rt.InferenceSession, rt.InferenceSession(self.model.onnx_definition))
        self._output_names = [output.name for output in self.sess.get_outputs()]

    def predict(self, payload: Base) -> Dict[str, List[Any]]:

        prediction = self._predict_and_extract(payload=payload)

        return prediction

    def _predict_and_extract(self, payload: Base) -> Dict[str, List[Any]]:
        """Creates prediction using onnx runtime
        Args:
            payload (Pydantic Base): Pydantic model containing features
        Returns:
            Prediction in the form ofa key value mapping
        """

        prediction = self.sess.run(
            output_names=self._output_names,
            input_feed=payload.to_onnx(),
        )

        return self._extract_predictions(prediction=prediction)

    def _extract_predictions(self, prediction: List[Any]) -> Dict[str, List[Any]]:
        """Parses onnx runtime prediction

        Args:
            Predictions (List): Onnx runtime prediction list

        Returns:
            Prediction in the form of a key value mapping
        """
        output_dict = {}

        for idx, output in enumerate(self._output_names):
            flat_pred = prediction[idx].flatten()
            output_dict[output] = list(flat_pred)

        return output_dict

    def _confirm_model_loaded(self):
        logger.info(
            "Model %s v%s successfully loaded",
            self.model.model_name,
            self.model.model_version,
        )


class ModelLoader:
    def __init__(self):

        self.model_path = os.getenv("OPSML_MODELAPI_JSON", "*model_def.json")
        self.model_files = self._get_model_files()

    def _get_model_files(self) -> List[str]:
        """Load model file from environment"""

        return list(set(glob.glob(f"**/**/{self.model_path}", recursive=True)))

    def load_models(self) -> List[Model]:
        """Load models"""
        models: List[Model] = []
        for model_path in self.model_files:
            model = Model(model_path)
            models.append(model)
        return models
