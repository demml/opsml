from functools import cached_property
from typing import Dict, cast

from opsml_artifacts.registry.cards.cards import (
    CardType,
    DataCard,
    ExperimentCard,
    ModelCard,
    PipelineCard,
)
from opsml_artifacts.registry.cards.types import (
    ArtifactStorageTypes,
    CardNames,
    StoragePath,
)
from opsml_artifacts.registry.data.formatter import ArrowTable, DataFormatter
from opsml_artifacts.registry.model.types import ModelApiDef
from opsml_artifacts.registry.storage.artifact_storage import (
    save_record_artifact_to_storage,
)
from opsml_artifacts.registry.storage.storage_system import StorageClientType
from opsml_artifacts.registry.storage.types import ArtifactStorageSpecs


class CardArtifactSaver:
    def __init__(self, card: CardType, storage_client: StorageClientType):
        """Parent class for saving artifacts belonging to cards

        Args:
            card (CardType): ArtifactCard with artifacts to save
            card_storage_info (ArtifactStorageSpecs): Extra info to use with artifact storage
        """

        self._card = card
        self.storage_client = storage_client

    @cached_property
    def card(self):
        return self.card

    def save_artifacts(self) -> CardType:
        raise NotImplementedError

    def _copy_artifact_storage_info(self) -> ArtifactStorageSpecs:
        """Copies artifact storage info"""

        return self.storage_client.storage_spec.copy(deep=True)

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(DataCard, self._card)

    def _convert_data_to_arrow(self) -> ArrowTable:
        """Converts data to arrow table

        Returns:
            arrow table model
        """
        arrow_table: ArrowTable = DataFormatter.convert_data_to_arrow(data=self.card.data)
        arrow_table.feature_map = DataFormatter.create_table_schema(arrow_table.table)

        return arrow_table

    def _save_pyarrow_table(self, arrow_table: ArrowTable) -> StoragePath:
        """Saves pyarrow table to file system

        Args:
            arrow_table (ArrowTable): Pyarrow table
        """
        storage_spec = self._copy_artifact_storage_info()
        storage_spec.filename = storage_spec.name
        self.storage_client.storage_spec = storage_spec
        storage_path = save_record_artifact_to_storage(
            artifact=arrow_table.table,
            storage_client=self.storage_client,
        )

        return storage_path

    def _set_arrow_card_attributes(self, arrow_table: ArrowTable):
        """Sets additional card attributes associated with arrow table"""
        self.card.data_uri = arrow_table.storage_uri
        self.card.feature_map = arrow_table.feature_map
        self.card.data_type = arrow_table.table_type

    def _save_data(self) -> None:
        """Saves DataCard data to file system"""

        arrow_table = self._convert_data_to_arrow()
        storage_path = self._save_pyarrow_table(arrow_table=arrow_table)
        arrow_table.storage_uri = storage_path.uri
        self._set_arrow_card_attributes(arrow_table=arrow_table)

    def _save_drift(self):
        """Saves a drift report to file system"""

        storage_spec = self._copy_artifact_storage_info()
        storage_spec.filename = "drift_report"
        self.storage_client.storage_spec = storage_spec
        storage_path = save_record_artifact_to_storage(
            artifact=self.card.drift_report,
            storage_client=self.storage_client,
        )
        self.card.drift_uri = storage_path.uri

    def save_artifacts(self):
        """Saves artifacts from a DataCard"""

        self._save_data()
        if bool(self.card.drift_report):
            self._save_drift()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.DATA in card_type


class ModelCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(ModelCard, self._card)

    def _get_onnx_model_def(self) -> ModelApiDef:
        """Create Onnx Model from trained model"""
        onnx_predictor = self.card.onnx_model(start_onnx_runtime=False)
        return onnx_predictor.get_api_model()

    def _save_api_definition(self):

        storage_spec = self._copy_artifact_storage_info()
        storage_spec.filename = "api-def"
        self.storage_client.storage_spec = storage_spec

        api_def = self._get_onnx_model_def()
        save_record_artifact_to_storage(
            artifact=api_def.json(),
            artifact_type=ArtifactStorageTypes.JSON.value,
            storage_client=self.storage_client,
        )

    def _save_modelcard(self):
        """Saves a modelcard to file system"""

        storage_spec = self._copy_artifact_storage_info()
        storage_spec.filename = "modelcard"
        self.storage_client.storage_spec = storage_spec

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.dict(exclude={"sample_input_data", "trained_model", "storage_client"}),
            storage_client=self.storage_client,
        )

        self.card.model_card_uri = storage_path.uri

    def _save_trained_model(self):
        """Saves trained model associated with ModelCard to filesystem"""

        storage_spec = self._copy_artifact_storage_info()
        storage_spec.filename = "trained-model"
        self.storage_client.storage_spec = storage_spec

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.trained_model,
            artifact_type=self.card.model_type,
            storage_client=self.storage_client,
        )
        self.card.trained_model_uri = storage_path.uri

    def _save_sample_data(self) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        storage_spec = self._copy_artifact_storage_info()
        storage_spec.filename = "sample-model-data"
        self.storage_client.storage_spec = storage_spec

        arrow_table: ArrowTable = DataFormatter.convert_data_to_arrow(data=self.card.sample_input_data)
        storage_path = save_record_artifact_to_storage(
            artifact=arrow_table.table,
            storage_client=self.storage_client,
        )
        self.card.sample_data_uri = storage_path.uri
        self.card.sample_data_type = arrow_table.table_type

    def save_artifacts(self):
        """Save model artifacts associated with ModelCard"""
        self._save_api_definition()
        self._save_modelcard()
        self._save_trained_model()
        self._save_sample_data()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.MODEL in card_type


class ExpeirmentCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(ExperimentCard, self._card)

    def save_artifacts(self) -> CardType:
        """Saves all artifacts associated with ExperimentCard to filesystem"""

        artifact_uris: Dict[str, str] = {}

        if self.card.artifacts is not None:
            for name, artifact in self.card.artifacts.items():
                storage_path = save_record_artifact_to_storage(
                    artifact=artifact,
                    storage_client=self.storage_client,
                )
                artifact_uris[name] = storage_path.uri
        self.card.artifact_uris = artifact_uris

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.EXPERIMENT in card_type


class PipelineCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(PipelineCard, self._card)

    def save_artifacts(self):
        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.PIPELINE in card_type


def save_card_artifacts(card: CardType, storage_client: StorageClientType) -> CardType:

    """Saves a given ArtifactCard's artifacts to a filesystem

    Args:
        card (ArtifactCard): ArtifactCard to save
        artifact_storage_info (ArtifactStorageSpecs): Extra storage info to associate
        with card.

    Returns:
        Modified ArtifactCard
    """
    card_saver = next(
        card_saver
        for card_saver in CardArtifactSaver.__subclasses__()
        if card_saver.validate(card_type=card.__class__.__name__.lower())
    )

    saver = card_saver(card=card, storage_client=storage_client)

    return saver.save_artifacts()
