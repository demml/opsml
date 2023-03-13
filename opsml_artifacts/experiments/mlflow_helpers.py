import tempfile
import mlflow
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
from opsml_artifacts import ModelCard
from opsml_artifacts.helpers.logging import ArtifactLogger

# Notes during development
# assume you are using mlflow url with a proxy client for artifacts
#  Add ApiRegistry with call paths to update opsml
# Needs: Absolute path for mlflow artifacts (base bucket path)

logger = ArtifactLogger.get_logger(__name__)
SKLEARN_FLAVOR = ["sklearn"]


class ModelCardLogger:
    def __init__(self, card: ModelCard, client: MlflowClient, run_id: str):
        self.client = client
        self.run_id = run_id
        self.card = card
        self.trained_model_path = "trained_model"
        self.onnx_model_path = "onnx_model"

    def _log_trained_model(self):
        if any(type_ in self.card.model_type for type_ in SKLEARN_FLAVOR):
            preds = self.card.trained_model.predict(self.card.sample_input_data)
            mlflow.sklearn.log_model(
                sk_model=self.card.trained_model,
                artifact_path=self.trained_model_path,
                signature=infer_signature(self.card.sample_input_data, preds),
            )

    def _log_onnx_model(self):
        api_def = self.card.onnx_model(start_onnx_runtime=False).get_api_model()
        with tempfile.NamedTemporaryFile(suffix=".json") as tmpfile:  # noqa
            tmpfile.write(api_def.json())
            self.client.log_artifact(
                run_id=self.run_id,
                local_path=tmpfile,
                artifact_path="onnx_model",
            )

    def log_model_artifacts(self):
        self._log_trained_model()
        self._log_onnx_model()
