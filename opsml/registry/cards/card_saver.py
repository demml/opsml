# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import tempfile
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast
from pydantic import BaseModel
import pyarrow as pa
from numpy.typing import NDArray
import json
import joblib
from opsml.registry.cards.audit import AuditCard
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.data import DataCard
from opsml.registry.cards.model import ModelCard
from opsml.registry.cards.pipeline import PipelineCard
from opsml.registry.cards.project import ProjectCard
from opsml.registry.cards.run import RunCard
from opsml.registry.data.formatter import DataFormatter
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.model.interfaces import SUPPORTED_MODELS, HuggingFaceModel
from opsml.registry.model.metadata_creator import _TrainedModelMetadataCreator
from opsml.registry.model.model_converters import _OnnxModelConverter
from opsml.registry.storage.artifact import save_artifact_to_storage
from opsml.registry.storage.client import StorageClientType
from opsml.registry.types import (
    AllowedDataType,
    ArrowTable,
    CardType,
    HuggingFaceStorageArtifact,
    ModelMetadata,
    OnnxAttr,
    SaveName,
    StorageRequest,
    UriNames,
    ValidSavedSample,
    CommonKwargs,
    DataDict,
)
from opsml.registry.types.extra import Suffix
from opsml.registry.storage import client


class CardUris(BaseModel):
    trained_model_uri: str = CommonKwargs.UNDEFINED.value
    preprocessor_uri: Optional[str] = None
    sample_data_uri: Optional[str] = None
    onnx_model_uri: Optional[str] = None


class CardArtifactSaver:
    def __init__(self, card: ArtifactCard):
        """
        Parent class for saving artifacts belonging to cards.
        ArtifactSaver controls pathing for all card objects

        Args:
            card:
                ArtifactCard with artifacts to save
            card_storage_info:
                Extra info to use with artifact storage
        """

        self._card = card
        self._card_uris = CardUris()

    @cached_property
    def card(self) -> ArtifactCard:
        return self.card

    def save_artifacts(self) -> Tuple[Any, Any]:
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

        storage_request = StorageRequest(
            registry_type=self.card.card_type,
            card_uid=self.card.uid,
            uri_name=UriNames.DATACARD_URI.value,
            filename=SaveName.DATACARD.value,
            uri_path=self.uris.get(
                UriNames.DATACARD_URI.value,
                Path(self.card.uri, SaveName.DATACARD.value),
            ),
        )

        storage_path = save_artifact_to_storage(
            artifact=self.card.model_dump(exclude=exclude_attr),
            storage_request=storage_request,
        )

        self.uris[UriNames.DATACARD_URI.value] = storage_path

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
        storage_request = (
            StorageRequest(
                registry_type=self.card.card_type,
                card_uid=self.card.uid,
                uri_name=UriNames.DATA_URI.value,
                filename=self.card.name,
                uri_path=self.uris.get(
                    UriNames.DATA_URI.value,
                    Path(self.card.uri, SaveName.DATA.value),
                ),
            ),
        )

        return save_artifact_to_storage(
            artifact=data,
            storage_request=storage_request,
            artifact_type=self.card.metadata.data_type,
        )

        return storage_path

    # TODO: steven - should be able to save tensorflow and torch datasets
    def _save_data(self) -> None:
        """Saves DataCard data to file system"""
        if self.card.data is None:
            return

        if isinstance(self.card.data, ImageDataset):
            self.card.data.convert_metadata()
            storage_path = self._save_data_to_storage(data=self.card.data)
            self.uris[UriNames.DATA_URI.value] = storage_path

        else:
            arrow_table: ArrowTable = self._convert_data_to_arrow()
            storage_path = self._save_data_to_storage(data=arrow_table.table)
            self.uris[UriNames.DATA_URI.value] = storage_path
            self.card.metadata.feature_map = arrow_table.feature_map

    def _save_profile(self) -> None:
        """Saves a datacard data profile"""
        if self.card.data_profile is None:
            return

        # profile report needs to be dumped to bytes and saved in joblib/pickle format
        # This is a requirement for loading with ydata-profiling
        profile_bytes = self.card.data_profile.dumps()

        storage_request = (
            StorageRequest(
                registry_type=self.card.card_type,
                card_uid=self.card.uid,
                uri_name=UriNames.PROFILE_URI.value,
                filename=SaveName.DATA_PROFILE.value,
                uri_path=self.uris.get(
                    UriNames.PROFILE_URI.value,
                    Path(self.card.uri, SaveName.PROFILE.value),
                ),
            ),
        )
        storage_path = save_artifact_to_storage(
            artifact=profile_bytes,
            storage_request=storage_request,
            artifact_type=AllowedDataType.JOBLIB.value,
        )
        self.uris[UriNames.PROFILE_URI.value] = storage_path

    def _save_profile_html(self) -> None:
        """Saves a profile report to file system"""
        if self.card.data_profile is None:
            return

        profile_html = self.card.data_profile.to_html()

        storage_request = (
            StorageRequest(
                registry_type=self.card.card_type,
                card_uid=self.card.uid,
                uri_name=UriNames.PROFILE_URI.value,
                filename=SaveName.DATA_PROFILE.value,
                uri_path=self.uris.get(
                    UriNames.PROFILE_HTML_URI.value,
                    Path(self.card.uri, SaveName.PROFILE.value),
                ),
            ),
        )

        storage_path = save_artifact_to_storage(
            artifact=profile_html,
            artifact_type=SaveName.HTML.value,
            storage_request=storage_request,
        )
        self.uris[UriNames.PROFILE_HTML_URI.value] = storage_path

    def save_artifacts(self) -> DataCard:
        """Saves artifacts from a DataCard"""

        self._save_data()
        self._save_profile()
        self._save_profile_html()

        self._save_datacard()

        return self.card, self.uris

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> ModelCard:
        return cast(ModelCard, self._card)

    def _save_model(self, path: Path) -> None:
        """Saves a model via model interface"""

        save_path = path / SaveName.TRAINED_MODEL
        saved_path = self.card.interface.save_model(save_path)
        self._card_uris.trained_model_uri = saved_path

    def _save_preprocessor(self, path: Path) -> None:
        """Save preprocessor via model interface"""

        if self.card.interface.preprocessor is not None:
            save_path = path / SaveName.PREPROCESSOR
            saved_path = self.card.interface.save_preprocessor(save_path)
            self._card_uris.preprocessor_uri = saved_path

    def _save_sample_data(self, path: Path) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        save_path = path / SaveName.SAMPLE_MODEL_DATA
        self.card.interface.save_sample_data(save_path)
        self._card_uris.sample_data_uri = save_path

    def _save_onnx_model(self, path: Path) -> None:
        if self.card.to_onnx is not None:
            save_path = path / SaveName.ONNX_MODEL
            metadata, saved_path = self.card.interface.convert_to_onnx(save_path)
        else:
            metadata = _TrainedModelMetadataCreator(self.card.interface).get_model_metadata()
            saved_path = None

        # set card data schema
        self.card.metadata.data_schema = metadata.data_schema
        self._card_uris.onnx_model_uri = saved_path

    def _get_model_metadata(self) -> ModelMetadata:
        """Create Onnx Model from trained model"""
        if self.card.interface.onnx_model is not None:
            onnx_version = self.card.interface.onnx_model.onnx_version
        else:
            onnx_version = None

        return ModelMetadata(
            model_name=self.card.name,
            model_type=self.card.interface.model_type,
            onnx_uri=self._card_uris.onnx_model_uri,
            onnx_version=onnx_version,
            model_uri=self._card_uris.trained_model_uri,
            model_version=self.card.version,
            model_team=self.card.team,
            data_schema=cast(DataDict, self.card.metadata.data_schema),
        )

    def _save_metadata(self, path: Path) -> None:
        model_metadata = self._get_model_metadata()

        # save model metadata to json
        save_path = Path(path / SaveName.MODEL_METADATA).with_suffix(Suffix.JSON.value)
        with save_path.open("w", encoding="utf-8") as target_file:
            json.dump(model_metadata.model_dump_json(), target_file)

    def _save_modelcard(self, path: Path) -> None:
        """Saves a modelcard to file system"""
        model_dump = self.card.model_dump(
            exclude={
                {"interface": {"model", "sample_data", "preprocessor", "onnx_model"}},
            }
        )

        save_path = Path(path / SaveName.MODELCARD).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(model_dump, save_path)

    def save_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            self._save_model(dir_path)
            self._save_preprocessor(dir_path)
            self._save_onnx_model(dir_path)
            self._save_sample_data(dir_path)
            self._save_metadata(dir_path)
            self._save_modelcard(dir_path)
            client.storage_client.put(dir_path, self.card.uri)

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
            storage_spec=self._get_storage_spec(
                filename=SaveName.AUDIT,
                uri=self.uris.get(UriNames.AUDIT_URI.value),
            ),
        )

        self.uris[UriNames.AUDIT_URI.value] = storage_path

    def save_artifacts(self) -> AuditCard:
        self._save_audit()

        return self.card, self.uris

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
            storage_spec=self._get_storage_spec(
                filename=SaveName.RUNCARD.value,
                uri=self.uris.get(UriNames.RUNCARD_URI.value),
            ),
        )
        self.uris[UriNames.RUNCARD_URI.value] = storage_path

    def _save_run_artifacts(self) -> None:
        """Saves all artifacts associated with RunCard to filesystem"""
        artifact_uris: Dict[str, str] = {}
        self.uris[UriNames.ARTIFACT_URIS.value]: Dict[str, str] = {}
        if self.card.artifact_uris is not None:
            # some cards have already been saved and thus have URIs already.
            # include them
            artifact_uris = self.card.artifact_uris

        if self.card.artifacts is not None:
            for name, artifact in self.card.artifacts.items():
                if name in artifact_uris:
                    continue

                storage_path = save_artifact_to_storage(
                    artifact=artifact,
                    storage_client=self.storage_client,
                    root_uri=self.card.artifact_uri,
                    filename=name,
                )

                artifact_uris[name] = storage_path
                self.uris[UriNames.ARTIFACT_URIS.value][name] = storage_path

        self.card.artifact_uris = artifact_uris

    def save_artifacts(self) -> RunCard:
        self._save_run_artifacts()
        self._save_runcard()

        return self.card, self.uris

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.RUNCARD.value in card_type


class PipelineCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> PipelineCard:
        return cast(PipelineCard, self._card)

    def save_artifacts(self) -> PipelineCard:
        return self.card, self.uris

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


def save_card_artifacts(
    card: ArtifactCard,
    storage_client: StorageClientType,
    uris: Optional[Dict[str, str]] = None,
) -> ArtifactCard:
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

    saver = card_saver(card=card, storage_client=storage_client, uris=uris)

    return saver.save_artifacts()  # type: ignore
