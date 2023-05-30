import os
from enum import Enum
from functools import cached_property
from typing import Dict, Optional, cast

from opsml.model.types import ModelMetadata, OnnxAttr
from opsml.registry.cards.cards import (
    ArtifactCard,
    DataCard,
    ModelCard,
    PipelineCard,
    ProjectCard,
    RunCard,
)
from opsml.registry.cards.types import CardType, StoragePath
from opsml.registry.data.formatter import ArrowTable, DataFormatter
from opsml.registry.storage.artifact_storage import save_record_artifact_to_storage
from opsml.registry.storage.storage_system import StorageClientType
from opsml.registry.storage.types import ArtifactStorageSpecs, ArtifactStorageType


class SaveName(str, Enum):
    DATACARD = "datacard"
    RUNCARD = "runcard"
    MODELCARD = "modelcard"
    PIPLELINECARD = "pipelinecard"
    MODEL_METADATA = "model-metadata"
    TRAINED_MODEL = "trained-model"
    SAMPLE_MODEL_DATA = "sample-model-data"
    DRIFT_REPORT = "drift_report"


class CardArtifactSaver:
    def __init__(self, card: ArtifactCard, storage_client: StorageClientType):
        """
        Parent class for saving artifacts belonging to cards

        Args:
            card:
                ArtifactCard with artifacts to save
            card_storage_info:
                Extra info to use with artifact storage
        """

        self._card = card
        self.storage_client = storage_client

    @cached_property
    def card(self):
        return self.card

    @property
    def save_path(self) -> str:
        return self.storage_client.storage_spec.save_path

    @save_path.setter
    def save_path(self, save_path: str) -> None:
        self.storage_client.storage_spec.save_path = save_path

    @property
    def storage_spec(self) -> ArtifactStorageSpecs:
        return self.storage_client.storage_spec

    def save_artifacts(self) -> ArtifactCard:
        raise NotImplementedError

    def _copy_artifact_storage_info(self) -> ArtifactStorageSpecs:
        """Copies artifact storage info"""

        return self.storage_client.storage_spec.copy(deep=True)

    def _set_storage_spec(self, filename: str, uri: Optional[str] = None) -> None:
        """
        Gets storage spec for saving

        Args:
            filename:
                Name of file
            uri:
                Optional uri. Assumes a card is being update if provided

        """
        storage_spec = self._copy_artifact_storage_info()
        storage_spec.filename = filename
        self.storage_client.storage_spec = storage_spec

        if uri is not None:
            self.save_path = self.resolve_path(uri=uri)

    def resolve_path(self, uri: str) -> str:
        """
        Resolve a file dir uri for card updates

        Args:
            uri:
                path to file
        Returns
            Resolved path string
        """

        dir_path = os.path.dirname(uri)
        return dir_path.split(f"{self.storage_client.base_path_prefix}/")[1]

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(DataCard, self._card)

    def _save_datacard(self):
        """Saves a datacard to file system"""

        self._set_storage_spec(
            filename=SaveName.DATACARD,
            uri=self.card.uris.datacard_uri,
        )

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.dict(exclude={"data", "storage_client"}),
            storage_client=self.storage_client,
        )

        self.card.uris.datacard_uri = storage_path.uri

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
        self._set_storage_spec(filename=self.card.name, uri=self.card.uris.data_uri)

        storage_path = save_record_artifact_to_storage(
            artifact=arrow_table.table,
            storage_client=self.storage_client,
        )

        return storage_path

    def _set_arrow_card_attributes(self, arrow_table: ArrowTable):
        """Sets additional card attributes associated with arrow table"""
        self.card.uris.data_uri = arrow_table.storage_uri
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

        self._set_storage_spec(
            filename=SaveName.DRIFT_REPORT,
            uri=self.card.uris.data_uri,
        )

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.drift_report,
            storage_client=self.storage_client,
        )
        self.card.drift_uri = storage_path.uri

    def save_artifacts(self):
        """Saves artifacts from a DataCard"""

        if self.card.data is not None:
            self._save_data()
        self._save_datacard()
        # drift not implemented yet
        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(ModelCard, self._card)

    def _get_model_metadata(self, onnx_attr: OnnxAttr) -> ModelMetadata:
        """Create Onnx Model from trained model"""

        return ModelMetadata(
            model_name=self.card.name,
            model_type=self.card.model_type,
            onnx_uri=onnx_attr.onnx_path,
            onnx_version=onnx_attr.onnx_version,
            model_uri=self.card.uris.trained_model_uri,
            model_version=self.card.version,
            sample_data=self.card._get_sample_data_for_api(),  # pylint: disable=protected-access
            data_schema=self.card.data_schema,
        )

    def _save_onnx_model(self) -> OnnxAttr:
        self._set_storage_spec(
            filename=f"{self.card.name}-v{self.card.version.replace('.', '-')}",
            uri=self.card.uris.model_metadata_uri,
        )
        # creates model metadata and onnx model (if to_onnx = True)
        self.card._create_and_set_model_attr(to_onnx=self.card.to_onnx)  # pylint: disable=protected-access

        if self.card.to_onnx:
            storage_path = save_record_artifact_to_storage(
                artifact=self.card.onnx_model_def.model_bytes,
                artifact_type=ArtifactStorageType.ONNX.value,
                storage_client=self.storage_client,
            )

            return OnnxAttr(
                onnx_path=storage_path.uri,
                onnx_version=self.card.onnx_model_def.onnx_version,
            )
        return OnnxAttr()

    def _save_model_metadata(self):
        onnx_attr = self._save_onnx_model()

        self._save_trained_model()
        self._save_sample_data()

        self._set_storage_spec(
            filename=SaveName.MODEL_METADATA,
            uri=self.card.uris.model_metadata_uri,
        )

        model_metadata = self._get_model_metadata(onnx_attr=onnx_attr)

        metadata_path = save_record_artifact_to_storage(
            artifact=model_metadata.json(),
            artifact_type=ArtifactStorageType.JSON.value,
            storage_client=self.storage_client,
        )

        self.card.uris.model_metadata_uri = metadata_path.uri

    def _save_modelcard(self):
        """Saves a modelcard to file system"""

        self._set_storage_spec(
            filename=SaveName.MODELCARD,
            uri=self.card.uris.modelcard_uri,
        )

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.dict(
                exclude={
                    "sample_input_data",
                    "trained_model",
                    "storage_client",
                    "onnx_model_def",
                }
            ),
            storage_client=self.storage_client,
        )

        self.card.uris.modelcard_uri = storage_path.uri

    def _save_trained_model(self):
        """Saves trained model associated with ModelCard to filesystem"""

        self._set_storage_spec(
            filename=SaveName.TRAINED_MODEL,
            uri=self.card.uris.trained_model_uri,
        )

        self.storage_spec.sample_data = self.card.sample_input_data

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.trained_model,
            artifact_type=self.card.model_type,
            storage_client=self.storage_client,
        )
        self.card.uris.trained_model_uri = storage_path.uri

    def _save_sample_data(self) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        self._set_storage_spec(
            filename=SaveName.SAMPLE_MODEL_DATA,
            uri=self.card.uris.sample_data_uri,
        )

        arrow_table: ArrowTable = DataFormatter.convert_data_to_arrow(data=self.card.sample_input_data)
        storage_path = save_record_artifact_to_storage(
            artifact=arrow_table.table,
            storage_client=self.storage_client,
        )

        self.card.uris.sample_data_uri = storage_path.uri
        self.card.sample_data_type = arrow_table.table_type

    def save_artifacts(self):
        """Save model artifacts associated with ModelCard"""
        self._save_model_metadata()
        self._save_modelcard()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type


class RunCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(RunCard, self._card)

    def _save_runcard(self):
        """Saves a runcard"""

        self._set_storage_spec(
            filename=SaveName.RUNCARD,
            uri=self.card.runcard_uri,
        )

        storage_path = save_record_artifact_to_storage(
            artifact=self.card.dict(exclude={"artifacts", "storage_client"}),
            storage_client=self.storage_client,
        )
        self.card.runcard_uri = storage_path.uri

    def _save_run_artifacts(self) -> None:
        """Saves all artifacts associated with RunCard to filesystem"""

        # check if artifacts have already been saved (Mlflow runs save artifacts during run)
        if self.card.artifact_uris is None:
            artifact_uris: Dict[str, str] = {}

            if self.card.artifacts is not None:
                for name, artifact in self.card.artifacts.items():
                    storage_path = save_record_artifact_to_storage(
                        artifact=artifact,
                        storage_client=self.storage_client,
                    )
                    artifact_uris[name] = storage_path.uri

            self.card.artifact_uris = artifact_uris

    def save_artifacts(self) -> ArtifactCard:
        self._save_run_artifacts()
        self._save_runcard()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.RUNCARD.value in card_type


class PipelineCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(PipelineCard, self._card)

    def save_artifacts(self):
        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.PIPELINECARD.value in card_type


class ProjectCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(ProjectCard, self._card)

    def save_artifacts(self):
        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.PROJECTCARD.value in card_type


def save_card_artifacts(card: ArtifactCard, storage_client: StorageClientType) -> ArtifactCard:
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
