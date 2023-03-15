import json
from typing import Dict
from opsml_artifacts.registry.cards.types import CardNames
from opsml_artifacts.registry.cards.cards import CardTypes
from opsml_artifacts.registry.sql.models import ArtifactStorageInfo
from opsml_artifacts.registry.cards.types import StoragePath
from opsml_artifacts.registry.data.formatter import ArrowTable, DataFormatter
from opsml_artifacts.registry.cards.artifact_storage import save_record_artifact_to_storage


class CardArtifactSaver:
    def __init__(
        self,
        card: CardTypes,
        card_storage_info: ArtifactStorageInfo,
    ):
        """Parent class for saving artifacts belonging to cards

        Args:
            card (CardType): ArtifactCard with artifacts to save
            card_storage_info (ArtifactStorageInfo): Extra info to use with artifact storage
        """

        self.card = card
        self.artifact_storage_info = card_storage_info

    def save_artifacts(self) -> CardTypes:
        raise NotImplementedError

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardArtifactSaver(CardArtifactSaver):
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
        storage_path = save_record_artifact_to_storage(
            artifact=arrow_table.table,
            artifact_storage_info=self.artifact_storage_info,
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

        self.artifact_storage_info.name = "drift_report"
        storage_path = save_record_artifact_to_storage(
            artifact=self.drift_report,
            artifact_storage_info=self.artifact_storage_info,
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
    def _copy_artifact_storage_info(self) -> ArtifactStorageInfo:
        """Copies artifact storage info"""

        return self.artifact_storage_info.copy(deep=True)

    def _save_modelcard(self):
        """Saves a modelcard to file system"""

        artifact_storage_info = self._copy_artifact_storage_info()
        artifact_storage_info.filename = f"modelcard"

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.dict(exclude={"sample_input_data", "trained_model", "storage_client"}),
            artifact_storage_info=artifact_storage_info,
        )

        self.card.model_card_uri = storage_path.uri

    def _save_trained_model(self):
        """Saves trained model associated with ModelCard to filesystem"""

        artifact_storage_info = self._copy_artifact_storage_info()
        artifact_storage_info.filename = f"trained-model"
        storage_path = save_record_artifact_to_storage(
            artifact=self.card.trained_model,
            artifact_storage_info=artifact_storage_info,
            artifact_type=self.card.model_type,
        )
        self.card.trained_model_uri = storage_path.uri

    def _save_sample_data(self):
        """Saves sample data associated with ModelCard to filesystem"""
        artifact_storage_info = self._copy_artifact_storage_info()
        artifact_storage_info.name = "sample-data"
        arrow_table: ArrowTable = DataFormatter.convert_data_to_arrow(data=self.card.sample_input_data)
        storage_path = save_record_artifact_to_storage(
            artifact=arrow_table.table,
            artifact_storage_info=artifact_storage_info,
        )
        self.card.sample_data_uri = storage_path.uri
        self.card.sample_data_type = arrow_table.table_type

    def _save_api_definition(self):
        artifact_storage_info = self._copy_artifact_storage_info()
        artifact_storage_info.name = "api-def"
        api_def = self.card.onnx_model(start_onnx_runtime=False).get_api_model()
        save_record_artifact_to_storage(
            artifact=json.loads(api_def.json()),  # replace this once pydantic v2 is released
            artifact_storage_info=artifact_storage_info,
        )

    def save_artifacts(self):
        """Save model artifacts associated with ModelCard"""
        self._save_modelcard()
        self._save_trained_model()
        self._save_sample_data()
        self._save_api_definition()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.MODEL in card_type


class ExpeirmentCardArtifactSaver(CardArtifactSaver):
    def save_artifacts(self):
        """Saves all artifacts associated with ExperimentCard to filesystem"""

        artifact_uris: Dict[str, str] = {}

        if self.card.artifacts is not None:
            for name, artifact in self.card.artifacts.items():
                storage_path = save_record_artifact_to_storage(
                    artifact=artifact,
                    artifact_storage_info=self.artifact_storage_info,
                )
                artifact_uris[name] = storage_path.uri
        self.card.artifact_uris = artifact_uris

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.EXPERIMENT in card_type


class PipelineCardArtifactSaver(CardArtifactSaver):
    def save_artifacts(self):
        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardNames.PIPELINE in card_type


def save_card_artifacts(
    card: CardTypes,
    artifact_storage_info: ArtifactStorageInfo,
) -> CardTypes:

    """Saves a given ArtifactCard's artifacts to a filesystem

    Args:
        card (ArtifactCard): ArtifactCard to save
        artifact_storage_info (ArtifactStorageInfo): Extra storage info to associate
        with card.

    Returns:
        Modified ArtifactCard
    """
    card_saver = next(
        card_saver
        for card_saver in CardArtifactSaver.__subclasses__()
        if card_saver.validate(card_type=card.__class__.__name__.lower())
    )

    saver = card_saver(
        card=card,
        card_storage_info=artifact_storage_info,
    )

    return saver.save_artifacts()
