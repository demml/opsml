from typing import Optional, Any
import tempfile
from pydantic import BaseModel
import mlflow
from enum import Enum
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
from mlflow.models import Model
from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.types import CardNames
from opsml_artifacts.registry.sql.registry import CardTypes
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.helpers.models import StorageClientInfo
import pathlib

# Notes during development
# assume you are using mlflow url with a proxy client for artifacts
#  Add ApiRegistry with call paths to update opsml
# Needs: Absolute path for mlflow artifacts (base bucket path)

logger = ArtifactLogger.get_logger(__name__)
SKLEARN_FLAVOR = ["sklearn"]

settings.set_storage(storage_info=StorageClientInfo())


class CardLogger:
    def __init__(self, card: CardTypes, client: MlflowClient, run_id: str):
        self.client = client
        self.run_id = run_id
        self.card = card

    def log_artifacts(self) -> None:
        raise NotImplementedError

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class ModelCardLogger(CardLogger):
    def __init__(self, card: CardTypes, client: MlflowClient, run_id: str):

        super().__init__(
            card=card,
            client=client,
            run_id=run_id,
        )
        self.trained_model_path = "trained_model"
        self.onnx_model_path = "onnx_model"

    def _log_trained_model(self):
        """Logs a trained model from a modelcard"""

        if any(type_ in self.card.model_type for type_ in SKLEARN_FLAVOR):
            MlFlowSklearn(
                trained_model=self.card.trained_model,
                sample_input_data=self.card.sample_input_data,
                model_path=self.trained_model_path,
                run_id=self.run_id,
                client=self.client,
            ).save_model()

    def _log_onnx_model(self):
        """Logs an onnx model definition from a modelcard"""

        api_def = self.card.onnx_model(start_onnx_runtime=False).get_api_model()
        api_def["model_version"] = self.card.version

        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = pathlib.Path(f"{tmpdirname}/model_def.json")

            with filepath.open("w", encoding="utf-8") as file_:
                file_.write(api_def.json())

            self.client.log_artifact(
                run_id=self.run_id,
                local_path=filepath,
                artifact_path="onnx_model",
            )

    def log_artifacts(self):
        self._log_trained_model()
        self._log_onnx_model()

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.MODEL.value in card_type


def log_card_artifacts(
    card_type: str,
    artifact_card: CardTypes,
    run_id: str,
    client: MlflowClient,
):

    logger: CardLogger = next(
        logger
        for logger in CardLogger.__subclasses__()
        if logger.validate(
            card_type=card_type,
        )
    )

    logger = logger(card=artifact_card, run_id=run_id, client=client)
    logger.log_artifacts()

    return logger


class MlFLowCardRegistries(BaseModel):
    datacard: CardRegistry
    modelcard: CardRegistry
    experimentcard: CardRegistry

    class Config:
        arbitrary_types_allowed = True


class MlFlowModelSaver:
    def __init__(
        self,
        trained_model: Any,
        sample_input_data: Any,
        model_path: str,
        run_id: str,
        client: MlflowClient,
    ):
        self.model_path = model_path
        self.run_id = run_id
        self.model = trained_model
        self.sample_data = sample_input_data
        self.client = client

    def _create_signature(self) -> mlflow.models.ModelSignature:
        preds = self.model.predict(self.sample_data)
        signature = infer_signature(self.sample_data, preds)

        return signature

    def _save_model(
        self,
        local_path: str,
        signature: mlflow.models.ModelSignature,
    ):
        raise NotImplementedError

    def save_model(self):
        signature = self._create_signature()

        with tempfile.TemporaryDirectory() as tmpdirname:
            local_path = f"{tmpdirname}/{self.trained_model_path}"
            self._save_model(
                local_path=local_path,
                signature=signature,
            )

            self.client.log_artifact(
                run_id=self.run_id,
                local_path=local_path,
            )


class MlFlowSklearn(MlFlowModelSaver):
    def _save_model(
        self,
        local_path: str,
        signature: mlflow.models.ModelSignature,
    ):
        mlflow_model = Model(
            artifact_path=self.model_path,
            run_id=self.run_id,
        )
        mlflow.sklearn.save_model(
            sk_model=self.model,
            path=local_path,
            mlflow_model=mlflow_model,
            signature=signature,
            serialization_format="cloudpickle",
        )
