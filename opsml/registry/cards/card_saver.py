# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from enum import Enum
from functools import cached_property
from typing import Any, Dict, Optional, Tuple, Union, cast

import numpy as np
import pyarrow as pa
from numpy.typing import NDArray

from opsml.model.types import (
    ModelMetadata,
    OnnxAttr,
    OnnxModelDefinition,
    ValidSavedSample,
)
from opsml.registry.cards.audit import AuditCard
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.data import DataCard
from opsml.registry.cards.model import ModelCard
from opsml.registry.cards.pipeline import PipelineCard
from opsml.registry.cards.project import ProjectCard
from opsml.registry.cards.run import RunCard
from opsml.registry.cards.types import CardType
from opsml.registry.data.formatter import DataFormatter
from opsml.registry.data.types import AllowedDataType, ArrowTable
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.storage.artifact import save_artifact_to_storage
from opsml.registry.storage.client import StorageClientType
from opsml.registry.storage.types import ArtifactStorageType


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

    def save_artifacts(self) -> Any:
        raise NotImplementedError

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def _save_datacard(self) -> None:
        """Saves a datacard to file system"""

        exclude_attr = {"data_profile", "storage_client"}

        # ImageDataSets use pydantic models for data
        if AllowedDataType.IMAGE not in self.card.metadata.data_type:
            exclude_attr.add("data")

        uri = save_artifact_to_storage(
            artifact=self.card.model_dump(exclude=exclude_attr),
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.DATACARD.value,
        )

        self.card.metadata.uris.datacard_uri = uri

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

    def _save_data_to_storage(self, data: Union[pa.Table, NDArray[Any], ImageDataset]) -> str:
        """Saves data to

        Args:
            data:
                either numpy array , pyarrow table or image dataset

        Returns:
            Data URI
        """
        artifact_type: Optional[ArtifactStorageType] = None
        if isinstance(data, pa.Table):
            artifact_type = ArtifactStorageType.PYARROW
        elif isinstance(data, np.ndarray):
            artifact_type = ArtifactStorageType.NUMPY
        elif isinstance(data, ImageDataset):
            artifact_type = ArtifactStorageType.IMAGE
        else:
            raise ValueError(f"Unable to save data. Unsupported data format: {type(data)}")

        return save_artifact_to_storage(
            artifact=data,
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=self.card.name,
            artifact_type=artifact_type,
        )

    def _save_data(self) -> None:
        """Saves DataCard data to file system"""
        if self.card.data is None:
            return

        if isinstance(self.card.data, ImageDataset):
            self.card.data.convert_metadata()
            uri = self._save_data_to_storage(data=self.card.data)
            self.card.metadata.uris.data_uri = uri

        else:
            arrow_table: ArrowTable = self._convert_data_to_arrow()
            uri = self._save_data_to_storage(data=arrow_table.table)
            self.card.metadata.uris.data_uri = uri
            self.card.metadata.feature_map = arrow_table.feature_map

    def _save_profile(self) -> None:
        """Saves a datacard data profile"""
        if self.card.data_profile is None:
            return

        # profile report needs to be dumped to bytes and saved in joblib/pickle format
        # This is a requirement for loading with ydata-profiling
        profile_bytes = self.card.data_profile.dumps()

        uri = save_artifact_to_storage(
            artifact=profile_bytes,
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.DATA_PROFILE.value,
        )
        self.card.metadata.uris.profile_uri = uri

    def _save_profile_html(self) -> None:
        """Saves a profile report to file system"""
        if self.card.data_profile is None:
            return

        profile_html = self.card.data_profile.to_html()

        uri = save_artifact_to_storage(
            artifact=profile_html,
            artifact_type=ArtifactStorageType.HTML,
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.DATA_PROFILE.value,
        )

        self.card.metadata.uris.profile_html_uri = uri

    def save_artifacts(self) -> DataCard:
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
    def card(self) -> ModelCard:
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
            sample_data=self.card.get_sample_data_for_api(),
            data_schema=self.card.metadata.data_schema,
        )

    def _save_onnx_model(self) -> OnnxAttr:
        self.card.create_and_set_model_attr()

        if self.card.to_onnx:
            model_def = cast(OnnxModelDefinition, self.card.metadata.onnx_model_def)

            uri = save_artifact_to_storage(
                artifact=model_def.model_bytes,
                artifact_type=ArtifactStorageType.ONNX,
                storage_client=self.storage_client,
                root_uri=os.path.join(self.card.uri, "onnx"),
                filename=SaveName.ONNX_MODEL.value,
            )
            self.card.metadata.uris.onnx_model_uri = uri

            return OnnxAttr(
                onnx_path=uri,
                onnx_version=model_def.onnx_version,
            )
        return OnnxAttr()

    def _save_model_metadata(self) -> None:
        onnx_attr = self._save_onnx_model()
        self._save_trained_model()
        self._save_sample_data()

        model_metadata = self._get_model_metadata(onnx_attr=onnx_attr)

        uri = save_artifact_to_storage(
            artifact=model_metadata.model_dump_json(),
            artifact_type=ArtifactStorageType.JSON.value,
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.MODEL_METADATA.value,
        )
        self.card.metadata.uris.model_metadata_uri = uri

    def _save_modelcard(self) -> None:
        """Saves a modelcard to file system"""

        model_dump = self.card.model_dump(
            exclude={
                "sample_input_data",
                "trained_model",
                "storage_client",
            }
        )
        model_dump["metadata"].pop("onnx_model_def")

        uri = save_artifact_to_storage(
            artifact=model_dump,
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.MODELCARD.value,
        )
        self.card.metadata.uris.modelcard_uri = uri

    def _save_trained_model(self) -> None:
        """Saves trained model associated with ModelCard to filesystem"""

        uri = save_artifact_to_storage(
            artifact=self.card.trained_model,
            artifact_type=self.card.metadata.model_type,
            storage_client=self.storage_client,
            root_uri=os.path.join(self.card.uri, "model"),
            filename=SaveName.TRAINED_MODEL.value,
        )
        self.card.metadata.uris.trained_model_uri = uri

    def _get_artifact_and_type(self) -> Tuple[ValidSavedSample, Optional[ArtifactStorageType]]:
        """Get artifact and artifact type to save"""

        if self.card.metadata.sample_data_type == AllowedDataType.DICT:
            return self.card.sample_input_data, None

        if self.card.metadata.sample_data_type in [AllowedDataType.PYARROW.value, AllowedDataType.PANDAS.value]:
            arrow_table: ArrowTable = DataFormatter.convert_data_to_arrow(
                data=self.card.sample_input_data,
                data_type=self.card.metadata.sample_data_type,
            )
            return arrow_table.table, ArtifactStorageType.PYARROW

        return self.card.sample_input_data, ArtifactStorageType.NUMPY

    def _save_sample_data(self) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        artifact, artifact_type = self._get_artifact_and_type()

        uri = save_artifact_to_storage(
            artifact=artifact,
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.SAMPLE_MODEL_DATA.value,
            artifact_type=artifact_type,
        )

        self.card.metadata.uris.sample_data_uri = uri

    def save_artifacts(self) -> ModelCard:
        """Save model artifacts associated with ModelCard"""

        # TODO(@damon): Determine if we should *always* save model_metadata
        if self.card.metadata.uris.model_metadata_uri is None:
            self._save_model_metadata()

        self._save_modelcard()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type


class AuditCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> AuditCard:
        return cast(AuditCard, self._card)

    def _save_audit(self) -> None:
        uri = save_artifact_to_storage(
            artifact=self.card.model_dump(),
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.AUDIT,
        )
        self.card.metadata.audit_uri = uri

    def save_artifacts(self) -> AuditCard:
        self._save_audit()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.AUDITCARD.value in card_type


class RunCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> RunCard:
        return cast(RunCard, self._card)

    def _save_runcard(self) -> None:
        """Saves a runcard"""

        uri = save_artifact_to_storage(
            artifact=self.card.model_dump(exclude={"artifacts", "storage_client"}),
            storage_client=self.storage_client,
            root_uri=self.card.uri,
            filename=SaveName.RUNCARD.value,
        )
        self.card.runcard_uri = uri

    def _save_run_artifacts(self) -> None:
        """Saves all artifacts associated with RunCard to filesystem"""
        artifact_uris: Dict[str, str] = {}

        if self.card.artifact_uris is not None:
            # some cards have already been saved and thus have URIs already.
            # include them
            artifact_uris = self.card.artifact_uris

        if self.card.artifacts is not None:
            for name, artifact in self.card.artifacts.items():
                if name in artifact_uris:
                    continue

                uri = save_artifact_to_storage(
                    artifact=artifact,
                    storage_client=self.storage_client,
                    root_uri=self.card.artifact_uri,
                    filename=name,
                )
                artifact_uris[name] = uri

        self.card.artifact_uris = artifact_uris

    def save_artifacts(self) -> RunCard:
        self._save_run_artifacts()
        self._save_runcard()

        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.RUNCARD.value in card_type


class PipelineCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> PipelineCard:
        return cast(PipelineCard, self._card)

    def save_artifacts(self) -> PipelineCard:
        return self.card

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.PIPELINECARD.value in card_type


class ProjectCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> ProjectCard:
        return cast(ProjectCard, self._card)

    def save_artifacts(self) -> ProjectCard:
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

    return saver.save_artifacts()  # type: ignore
