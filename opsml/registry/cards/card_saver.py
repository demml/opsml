# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import tempfile
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast

import joblib
import pyarrow as pa
from numpy.typing import NDArray
from pydantic import BaseModel

from opsml.registry.cards.audit import AuditCard
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.data import DataCard
from opsml.registry.cards.model import ModelCard
from opsml.registry.cards.pipeline import PipelineCard
from opsml.registry.cards.project import ProjectCard
from opsml.registry.cards.run import RunCard
from opsml.registry.data.formatter import DataFormatter
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.model.metadata_creator import _TrainedModelMetadataCreator
from opsml.registry.storage import client
from opsml.registry.storage.artifact import save_artifact_to_storage
from opsml.registry.types import (
    AllowedDataType,
    ArrowTable,
    CardType,
    ModelMetadata,
    SaveName,
    UriNames,
)
from opsml.registry.types.extra import Suffix


class CardUris(BaseModel):
    data_uri: Optional[Path] = None
    trained_model_uri: Optional[Path] = None
    preprocessor_uri: Optional[Path] = None
    sample_data_uri: Optional[Path] = None
    onnx_model_uri: Optional[Path] = None

    lpath: Optional[Path] = None
    rpath: Optional[Path] = None

    def resolve_path(self, name: str) -> str:
        curr_path: Optional[Path] = getattr(self, name)

        if curr_path is None:
            return None

        assert self.lpath is not None and self.rpath is not None

        resolved_path = self.rpath / curr_path.relative_to(self.lpath)
        return str(resolved_path)


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
        self.card_uris = CardUris()
        self.storage_client = client.storage_client

    @cached_property
    def lpath(self) -> Path:
        assert self.card_uris.lpath is not None
        return self.card_uris.lpath

    @cached_property
    def rpath(self) -> Path:
        assert self.card_uris.rpath is not None
        return self.card_uris.rpath

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

    def _save_data(self) -> None:
        """Saves a data via data interface"""

        save_path = self.lpath / SaveName.DATA.value
        _ = self.card.interface.save_data(save_path)

        # set feature map on metadata
        self.card.metadata.feature_map = self.card.interface.feature_map

    def _save_data_profile(self) -> None:
        """Saves a data profile"""

        if self.card.data_profile is None:
            return

        save_path = self.lpath / SaveName.DATA_PROFILE.value

        # save html and joblib version
        _ = self.card.interface.save_data_profile(save_path, save_type="html")
        _ = self.card.interface.save_data_profile(save_path, save_type="joblib")

    def _save_datacard(self) -> None:
        """Saves a datacard to file system"""

        exclude_attr = {"interface": {"data", "data_profile"}}

        dumped_datacard = self.card.model_dump(exclude=exclude_attr)

        save_path = Path(self.lpath / SaveName.DATACARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_datacard, save_path)

    def save_artifacts(self) -> DataCard:
        """Saves artifacts from a DataCard"""

        # set type needed for loading
        self.card.metadata.interface_type = self.card.interface.__class__.__name__

        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_data()
            self._save_data_profile()
            self._save_datacard()
            self.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelCardArtifactSaver(CardArtifactSaver):
    @cached_property
    def card(self) -> ModelCard:
        return cast(ModelCard, self._card)

    def _save_model(self) -> None:
        """Saves a model via model interface"""

        save_path = self.lpath / SaveName.TRAINED_MODEL.value
        saved_path = self.card.interface.save_model(save_path)
        self.card_uris.trained_model_uri = saved_path

    def _save_preprocessor(self) -> None:
        """Save preprocessor via model interface"""

        if self.card.interface.preprocessor is not None:
            save_path = self.lpath / SaveName.PREPROCESSOR.value
            saved_path = self.card.interface.save_preprocessor(save_path)
            self.card_uris.preprocessor_uri = saved_path

    def _save_sample_data(self) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        save_path = self.lpath / SaveName.SAMPLE_MODEL_DATA.value
        saved_path = self.card.interface.save_sample_data(save_path)
        self.card_uris.sample_data_uri = saved_path

    def _save_onnx_model(self) -> None:
        if self.card.to_onnx is not None:
            save_path = self.lpath / SaveName.ONNX_MODEL.value
            metadata, saved_path = self.card.interface.convert_to_onnx(save_path)
        else:
            metadata = _TrainedModelMetadataCreator(self.card.interface).get_model_metadata()
            saved_path = None

        # set card data schema
        self.card.metadata.data_schema = metadata.data_schema
        self.card_uris.onnx_model_uri = saved_path

    def _get_model_metadata(self) -> ModelMetadata:
        """Create Onnx Model from trained model"""
        if self.card.interface.onnx_model is not None:
            onnx_version = self.card.interface.onnx_model.onnx_version
        else:
            onnx_version = None

        return ModelMetadata(
            model_name=self.card.name,
            model_class=self.card.interface.model_class,
            model_type=self.card.interface.model_type,
            model_interface=self.card.interface.__class__.__name__,
            onnx_uri=self.card_uris.resolve_path(UriNames.ONNX_MODEL_URI.value),
            onnx_version=onnx_version,
            model_uri=self.card_uris.resolve_path(UriNames.TRAINED_MODEL_URI.value),
            model_version=self.card.version,
            model_team=self.card.team,
            data_schema=self.card.metadata.data_schema,
        )

    def _save_metadata(self) -> None:
        model_metadata = self._get_model_metadata()

        # save model metadata to json
        save_path = Path(self.lpath / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
        save_path.write_text(model_metadata.model_dump_json())

    def _save_modelcard(self) -> None:
        """Saves a modelcard to file system"""

        dumped_model = self.card.model_dump(
            exclude={
                "interface": {"model", "preprocessor", "sample_data", "onnx_model"},
            }
        )

        save_path = Path(self.lpath / SaveName.MODELCARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_model, save_path)

    def save_artifacts(self):
        # set type needed for loading
        self.card.metadata.interface_type = self.card.interface.__class__.__name__

        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri

            self._save_model()
            self._save_preprocessor()
            self._save_onnx_model()
            self._save_sample_data()
            self._save_modelcard()
            self._save_metadata()
            self.storage_client.put(self.lpath, self.rpath)

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


def save_card_artifacts(card: ArtifactCard) -> ArtifactCard:
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

    saver = card_saver(card=card)

    return saver.save_artifacts()  # type: ignore
