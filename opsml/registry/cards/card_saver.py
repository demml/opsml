# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import tempfile
from functools import cached_property
from pathlib import Path
from typing import Optional, cast

import joblib
from pydantic import BaseModel

from opsml.registry.cards.audit import AuditCard
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.data import DataCard
from opsml.registry.cards.model import ModelCard
from opsml.registry.cards.pipeline import PipelineCard
from opsml.registry.cards.project import ProjectCard
from opsml.registry.cards.run import RunCard
from opsml.registry.model.interfaces.huggingface import HuggingFaceModel
from opsml.registry.model.onnx.metadata_creator import _TrainedModelMetadataCreator
from opsml.registry.storage import client
from opsml.registry.types import CardType, ModelMetadata, SaveName, UriNames
from opsml.registry.types.extra import Suffix


class CardUris(BaseModel):
    data_uri: Optional[Path] = None
    trained_model_uri: Optional[Path] = None
    preprocessor_uri: Optional[Path] = None
    sample_data_uri: Optional[Path] = None
    onnx_model_uri: Optional[Path] = None
    quantized_model_uri: Optional[Path] = None

    lpath: Optional[Path] = None
    rpath: Optional[Path] = None

    def resolve_path(self, name: str) -> str:
        curr_path: Optional[Path] = getattr(self, name)

        if curr_path is None:
            return None

        assert self.lpath is not None and self.rpath is not None

        resolved_path = self.rpath / curr_path.relative_to(self.lpath)
        return str(resolved_path)


class CardSaver:
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

    def save_artifacts(self) -> None:
        raise NotImplementedError

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardSaver(CardSaver):
    @cached_property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def _save_data(self) -> None:
        """Saves a data via data interface"""

        if self.card.interface.data is None:
            return None

        save_path = (self.lpath / SaveName.DATA.value).with_suffix(self.card.interface.data_suffix)
        self.card.interface.save_data(save_path)

        # set feature map on metadata
        self.card.metadata.feature_map = self.card.interface.feature_map

    def _save_data_profile(self) -> None:
        """Saves a data profile"""

        if self.card.interface.data_profile is None:
            return

        save_path = self.lpath / SaveName.DATA_PROFILE.value

        # save html and joblib version
        self.card.interface.save_data_profile(save_path.with_suffix(Suffix.HTML.value))
        self.card.interface.save_data_profile(save_path.with_suffix(Suffix.JOBLIB.value))

    def _save_datacard(self) -> None:
        """Saves a datacard to file system"""

        exclude_attr = {"interface": {"data", "data_profile"}}

        dumped_datacard = self.card.model_dump(exclude=exclude_attr)

        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_datacard, save_path)

    def save_artifacts(self) -> None:
        """Saves artifacts from a DataCard"""

        # quick checks
        if self.card.interface is None:
            raise ValueError("DataCard must have a data interface to save artifacts")

        if self.card.interface.data is None and not bool(self.card.interface.sql_logic):
            raise ValueError("DataInterface must have data or sql logic")

        # set type needed for loading
        self.card.metadata.interface_type = self.card.interface.__class__.__name__
        self.card.metadata.data_type = self.card.interface.data_type

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


class ModelCardSaver(CardSaver):
    @cached_property
    def card(self) -> ModelCard:
        return cast(ModelCard, self._card)

    def _save_model(self) -> None:
        """Saves a model via model interface"""

        save_path = (self.lpath / SaveName.TRAINED_MODEL.value).with_suffix(self.card.interface.model_suffix)

        self.card.interface.save_model(save_path)
        self.card_uris.trained_model_uri = save_path

    def _save_preprocessor(self) -> None:
        """Save preprocessor via model interface"""

        if self.card.interface.preprocessor is not None:
            save_path = (self.lpath / SaveName.PREPROCESSOR.value).with_suffix(self.card.interface.preprocessor_suffix)
            self.card.interface.save_preprocessor(save_path)
            self.card_uris.preprocessor_uri = save_path

    def _save_sample_data(self) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        save_path = (self.lpath / SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
        self.card.interface.save_sample_data(save_path)
        self.card_uris.sample_data_uri = save_path

    def _save_onnx_model(self) -> None:
        if self.card.to_onnx:
            save_path = (self.lpath / SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value)
            metadata = self.card.interface.convert_to_onnx(save_path)

            if isinstance(self.card.interface, HuggingFaceModel):
                assert self.card.interface.onnx_args is not None, "onnx_args must be set for HuggingFaceModel"
                if self.card.interface.onnx_args.quantize:
                    self.card_uris.quantized_model_uri = self.lpath / SaveName.QUANTIZED_MODEL.value

                # remove suffix for uris
                save_path = save_path.with_suffix("")

        else:
            metadata = _TrainedModelMetadataCreator(self.card.interface).get_model_metadata()
            save_path = None

        self.card.metadata.data_schema = metadata.data_schema
        self.card_uris.onnx_model_uri = save_path

    def _get_model_metadata(self) -> ModelMetadata:
        """Create Onnx Model from trained model"""
        if self.card.interface.onnx_model is not None:
            onnx_version = self.card.interface.onnx_model.onnx_version
        else:
            onnx_version = None

        metadata = ModelMetadata(
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

        # in case of huggingface quantized model, we add extra metadata
        if self.card_uris.quantized_model_uri is not None:
            metadata.quantized_model_uri = self.card_uris.resolve_path(UriNames.QUANTIZED_MODEL_URI.value)

        return metadata

    def _save_metadata(self) -> None:
        model_metadata = self._get_model_metadata()

        # save model metadata to json
        save_path = Path(self.lpath / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
        save_path.write_text(model_metadata.model_dump_json())

    def _save_modelcard(self) -> None:
        """Saves a modelcard to file system"""

        dumped_model = self.card.model_dump(
            exclude={
                "interface": {
                    "model",
                    "preprocessor",
                    "sample_data",
                    "onnx_model",
                },
            }
        )
        if dumped_model["interface"].get("onnx_args") is not None:
            dumped_model["interface"]["onnx_args"].pop("config")

        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_model, save_path)

    def save_artifacts(self) -> None:
        if self.card.interface is None:
            raise ValueError("ModelCard must have a data interface to save artifacts")

        # set type needed for loading
        self.card.metadata.interface_type = self.card.interface.__class__.__name__
        self.card.interface.modelcard_uid = str(self.card.uid)

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


class AuditCardSaver(CardSaver):
    @cached_property
    def card(self) -> AuditCard:
        return cast(AuditCard, self._card)

    def _save_auditcard(self) -> None:
        dumped_audit = self.card.model_dump()
        save_path = Path(self.lpath, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_audit, save_path)

    def save_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_auditcard()
            self.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.AUDITCARD.value in card_type


class RunCardSaver(CardSaver):
    @cached_property
    def card(self) -> RunCard:
        return cast(RunCard, self._card)

    def _save_runcard(self) -> None:
        """Saves a runcard"""

        dumped_audit = self.card.model_dump()
        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_audit, save_path)

    def save_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_runcard()
            self.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.RUNCARD.value in card_type


class PipelineCardSaver(CardSaver):
    @cached_property
    def card(self) -> PipelineCard:
        return cast(PipelineCard, self._card)

    def _save_pipelinecard(self) -> None:
        dumped_audit = self.card.model_dump()
        save_path = Path(self.lpath, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_audit, save_path)

    def save_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_pipelinecard()
            self.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.PIPELINECARD.value in card_type


class ProjectCardSaver(CardSaver):
    @cached_property
    def card(self) -> ProjectCard:
        return cast(ProjectCard, self._card)

    def _save_projectcard(self) -> None:
        dumped_audit = self.card.model_dump()
        save_path = Path(self.lpath, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_audit, save_path)

    def save_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_projectcard()
            self.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.PROJECTCARD.value in card_type


def save_card_artifacts(card: ArtifactCard) -> None:
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
        card_saver for card_saver in CardSaver.__subclasses__() if card_saver.validate(card_type=card.card_type)
    )

    saver = card_saver(card=card)

    return saver.save_artifacts()  # type: ignore
