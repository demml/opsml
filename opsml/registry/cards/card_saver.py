# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Dict, Optional, Union, cast

import numpy as np
import pyarrow as pa

from opsml.model.types import ModelMetadata, OnnxAttr
from opsml.registry.cards import (
    ArtifactCard,
    AuditCard,
    DataCard,
    ModelCard,
    PipelineCard,
    ProjectCard,
    RunCard,
)
from opsml.registry.cards.types import CardType, StoragePath
from opsml.registry.data.formatter import ArrowTable, DataFormatter
from opsml.registry.data.types import AllowedTableTypes, AllowedDataType
from opsml.registry.image import ImageDataset
from opsml.registry.storage.artifact_storage import save_artifact_to_storage
from opsml.registry.storage.storage_system import StorageClientType
from opsml.registry.storage.types import ArtifactStorageSpecs, ArtifactStorageType


class SaveName(str, Enum):
    DATACARD = "datacard"
    RUNCARD = "runcard"
    MODELCARD = "modelcard"
    AUDIT = "audit"
    PIPLELINECARD = "pipelinecard"
    MODEL_METADATA = "model-metadata"
    TRAINED_MODEL = "trained-model"
    ONNX_MODEL = "model"
    SAMPLE_MODEL_DATA = "sample-model-data"
    DATA_PROFILE = "data-profile"


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
    def card(self) -> ArtifactCard:
        return self.card

    def save_artifacts(self) -> ArtifactCard:
        raise NotImplementedError

    def _get_storage_spec(self, filename: str, uri: Optional[str] = None) -> ArtifactStorageSpecs:
        """
        Gets storage spec for saving

        Args:
            uri:
                Base URI to write the file to
            filename:
                Name of file

        """
        if uri is None:
            return ArtifactStorageSpecs(save_path=str(self.card.uri), filename=filename)

        return ArtifactStorageSpecs(save_path=self._resolve_dir(uri), filename=filename)

    def _resolve_dir(self, uri: str) -> str:
        """
        Resolve a file dir uri for card updates

        Args:
            uri:
                path to file
        Returns
            Resolved uri *directory* relative to the card.
        """
        base_path = Path(self.storage_client.base_path_prefix)
        uri_path = Path(uri).parent
        return str(uri_path.relative_to(base_path))

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(DataCard, self._card)

    def _save_datacard(self):
        """Saves a datacard to file system"""

        exclude_attr = {"data_profile", "storage_client"}

        # ImageDataSets use pydantic models for data
        if AllowedDataType.IMAGE not in self.card.metadata.data_type:
            exclude_attr.add("data")

        spec = self._get_storage_spec(
            filename=SaveName.DATACARD.value,
            uri=self.card.metadata.uris.datacard_uri,
        )
        storage_path = save_artifact_to_storage(
            artifact=self.card.model_dump(exclude=exclude_attr),
            storage_client=self.storage_client,
            storage_spec=spec,
        )

        self.card.metadata.uris.datacard_uri = storage_path.uri

    def _convert_data_to_arrow(self) -> ArrowTable:
        """Converts data to arrow table

        Returns:
            arrow table model
        """
        arrow_table: ArrowTable = DataFormatter.convert_data_to_arrow(
            data=self.card.data,
            data_type=self.card.metadata.data_type,
        )
        arrow_table.feature_map = DataFormatter.create_table_schema(data=self.card.data)
        return arrow_table

    def _save_data_to_storage(self, data: Union[pa.Table, np.ndarray, ImageDataset]) -> StoragePath:
        """Saves pyarrow table to file system

        Args:
            data:
                either numpy array , pyarrow table or image dataset

        Returns:
            StoragePath
        """

        storage_path = save_artifact_to_storage(
            artifact=data,
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=self.card.name,
                uri=self.card.metadata.uris.data_uri,
            ),
        )

        return storage_path

    def _save_data(self) -> None:
        """Saves DataCard data to file system"""
        if self.card.data is None:
            return

        if isinstance(self.card.data, ImageDataset):
            self.card.data.convert_metadata()
            storage_path = self._save_data_to_storage(data=self.card.data)
            self.card.metadata.uris.data_uri = storage_path.uri
            self.card.metadata.data_type = AllowedTableTypes.IMAGE_DATASET

        else:
            arrow_table: ArrowTable = self._convert_data_to_arrow()
            storage_path = self._save_data_to_storage(data=arrow_table.table)
            self.card.metadata.uris.data_uri = storage_path.uri
            self.card.metadata.feature_map = arrow_table.feature_map
            self.card.metadata.data_type = arrow_table.table_type

    def _save_profile(self) -> None:
        """Saves a datacard data profile"""
        if self.card.data_profile is None:
            return

        # profile report needs to be dumped to bytes and saved in joblib/pickle format
        # This is a requirement for loading with ydata-profiling
        profile_bytes = self.card.data_profile.dumps()

        storage_path = save_artifact_to_storage(
            artifact=profile_bytes,
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=SaveName.DATA_PROFILE.value,
                uri=self.card.metadata.uris.profile_uri,
            ),
        )
        self.card.metadata.uris.profile_uri = storage_path.uri

    def _save_profile_html(self) -> None:
        """Saves a profile report to file system"""
        if self.card.data_profile is None:
            return

        profile_html = self.card.data_profile.to_html()

        storage_path = save_artifact_to_storage(
            artifact=profile_html,
            artifact_type=ArtifactStorageType.HTML.value,
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=SaveName.DATA_PROFILE.value,
                uri=self.card.metadata.uris.profile_html_uri,
            ),
        )
        self.card.metadata.uris.profile_html_uri = storage_path.uri

    def save_artifacts(self):
        """Saves artifacts from a DataCard"""

        self._save_data()
        self._save_profile()
        self._save_profile_html()

        self._save_datacard()

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
            model_type=self.card.metadata.model_type,
            onnx_uri=onnx_attr.onnx_path,
            onnx_version=onnx_attr.onnx_version,
            model_uri=self.card.metadata.uris.trained_model_uri,
            model_version=self.card.version,
            model_team=self.card.team,
            sample_data=self.card._get_sample_data_for_api(),  # pylint: disable=protected-access
            data_schema=self.card.metadata.data_schema,
        )

    def _save_onnx_model(self) -> OnnxAttr:
        self.card._create_and_set_model_attr()  # pylint: disable=protected-access

        if self.card.to_onnx:
            storage_path = save_artifact_to_storage(
                artifact=self.card.metadata.onnx_model_def.model_bytes,
                artifact_type=ArtifactStorageType.ONNX.value,
                storage_client=self.storage_client,
                storage_spec=self._get_storage_spec(
                    filename=SaveName.ONNX_MODEL.value,
                    uri=self.card.metadata.uris.onnx_model_uri,
                ),
                extra_path="onnx",
            )

            self.card.metadata.uris.onnx_model_uri = storage_path.uri

            return OnnxAttr(
                onnx_path=storage_path.uri,
                onnx_version=self.card.metadata.onnx_model_def.onnx_version,
            )
        return OnnxAttr()

    def _save_model_metadata(self):
        onnx_attr = self._save_onnx_model()
        self._save_trained_model()
        self._save_sample_data()

        model_metadata = self._get_model_metadata(onnx_attr=onnx_attr)

        metadata_path = save_artifact_to_storage(
            artifact=model_metadata.model_dump_json(),
            artifact_type=ArtifactStorageType.JSON.value,
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=SaveName.MODEL_METADATA.value,
                uri=self.card.metadata.uris.model_metadata_uri,
            ),
        )

        self.card.metadata.uris.model_metadata_uri = metadata_path.uri

    def _save_modelcard(self):
        """Saves a modelcard to file system"""

        model_dump = self.card.model_dump(
            exclude={
                "sample_input_data",
                "trained_model",
                "storage_client",
            }
        )
        model_dump["metadata"].pop("onnx_model_def")

        storage_path = save_artifact_to_storage(
            artifact=model_dump,
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=SaveName.MODELCARD.value,
                uri=self.card.metadata.uris.modelcard_uri,
            ),
        )

        self.card.metadata.uris.modelcard_uri = storage_path.uri

    def _save_trained_model(self):
        """Saves trained model associated with ModelCard to filesystem"""

        storage_path = save_artifact_to_storage(
            artifact=self.card.trained_model,
            artifact_type=self.card.metadata.model_type,
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=SaveName.TRAINED_MODEL.value,
                uri=self.card.metadata.uris.trained_model_uri,
            ),
            extra_path="model",
        )
        self.card.metadata.uris.trained_model_uri = storage_path.uri

    def _save_sample_data(self) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        storage_spec = self._get_storage_spec(
            filename=SaveName.SAMPLE_MODEL_DATA.value,
            uri=self.card.metadata.uris.sample_data_uri,
        )

        if isinstance(self.card.sample_input_data, dict):
            storage_path = save_artifact_to_storage(
                artifact=self.card.sample_input_data,
                storage_client=self.storage_client,
                storage_spec=storage_spec,
            )
            self.card.metadata.sample_data_type = AllowedTableTypes.DICTIONARY.value

        else:
            arrow_table: ArrowTable = DataFormatter.convert_data_to_arrow(data=self.card.sample_input_data)
            storage_path = save_artifact_to_storage(
                artifact=arrow_table.table,
                storage_client=self.storage_client,
                storage_spec=storage_spec,
            )
            self.card.metadata.sample_data_type = arrow_table.table_type

        self.card.metadata.uris.sample_data_uri = storage_path.uri

    def save_artifacts(self):
        """Save model artifacts associated with ModelCard"""

        if self.card.metadata.uris.model_metadata_uri is None:
            self._save_model_metadata()

        self._save_modelcard()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type


class AuditCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(AuditCard, self._card)

    def _save_audit(self):
        storage_path = save_artifact_to_storage(
            artifact=self.card.model_dump(),
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=SaveName.AUDIT,
                uri=self.card.metadata.audit_uri,
            ),
        )

        self.card.metadata.audit_uri = storage_path.uri

    def save_artifacts(self) -> ArtifactCard:
        self._save_audit()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.AUDITCARD.value in card_type


class RunCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self):
        return cast(RunCard, self._card)

    def _save_runcard(self):
        """Saves a runcard"""
        storage_path = save_artifact_to_storage(
            artifact=self.card.model_dump(exclude={"artifacts", "storage_client"}),
            storage_client=self.storage_client,
            storage_spec=self._get_storage_spec(
                filename=SaveName.RUNCARD.value,
                uri=self.card.runcard_uri,
            ),
        )
        self.card.runcard_uri = storage_path.uri

    def _save_run_artifacts(self) -> None:
        """Saves all artifacts associated with RunCard to filesystem"""
        #
        # TODO(@damon): See where `.artifacts` are used. When
        # `ActiveRun.log_artifact` is called, the artifact is saved and *not*
        # added to `artifacts` on the runcard. We probably want to do either one
        # or the other - save the artifact when `log_artifact` is called *or*
        # here when the card is saved,rather than support both.
        #
        if self.card.artifact_uris is None:
            artifact_uris: Dict[str, str] = {}
        else:
            artifact_uris = self.card.artifact_uris

        if self.card.artifacts is not None:
            for name, artifact in self.card.artifacts.items():
                if name in artifact_uris:
                    continue
                storage_path = save_artifact_to_storage(
                    artifact=artifact,
                    storage_client=self.storage_client,
                    storage_spec=ArtifactStorageSpecs(save_path=str(self.card.artifact_uri), filename=name),
                )
                artifact_uris[name] = storage_path.uri

        run_card = cast(RunCard, self.card)
        run_card.artifact_uris = artifact_uris

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
        card:
            ArtifactCard to save
        storage_client:
            StorageClient to use to save artifacts

    Returns:
        ArtifactCard with updated artifact uris

    """
    card_saver = next(
        card_saver
        for card_saver in CardArtifactSaver.__subclasses__()
        if card_saver.validate(card_type=card.__class__.__name__.lower())
    )

    saver = card_saver(card=card, storage_client=storage_client)

    return saver.save_artifacts()
