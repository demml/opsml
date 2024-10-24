# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import tempfile
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import joblib
import yaml
from pydantic import BaseModel

from opsml.cards import (
    AuditCard,
    Card,
    DataCard,
    ModelCard,
    PipelineCard,
    ProjectCard,
    RunCard,
)
from opsml.data import DataInterface, Dataset
from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.huggingface import HuggingFaceModel
from opsml.model.metadata_creator import _TrainedModelMetadataCreator
from opsml.storage import client
from opsml.types import (
    AllowedDataType,
    CardType,
    ModelMetadata,
    SaveName,
    Suffix,
    UriNames,
)
from opsml.types.model import HuggingFaceOnnxArgs

logger = ArtifactLogger.get_logger()


# get root dir
MODEL_SCHEMA = Path(__file__).parents[0] / "schemas" / "modelcard.yaml"


class ModelCardSchema:
    """Helper class for defining include logic for saving modelcards"""

    @staticmethod
    def get_schema() -> List[str]:
        with MODEL_SCHEMA.open("r") as file_:
            try:
                model_schema: Dict[str, List[str]] = yaml.safe_load(file_)
                return model_schema["keys"]
            except yaml.YAMLError as error:
                logger.error(error)
                raise error


class CardUris(BaseModel):
    data_uri: Optional[Path] = None
    trained_model_uri: Optional[Path] = None
    preprocessor_uri: Optional[Path] = None
    sample_data_uri: Optional[Path] = None
    onnx_model_uri: Optional[Path] = None
    quantized_model_uri: Optional[Path] = None
    tokenizer_uri: Optional[Path] = None
    feature_extractor_uri: Optional[Path] = None
    onnx_config_uri: Optional[Path] = None
    drift_profile_uri: Optional[Path] = None

    lpath: Optional[Path] = None
    rpath: Optional[Path] = None

    def resolve_path(self, name: str) -> Optional[str]:
        """Resolves a path to a given artifact

        Args:
            name:
                Name of artifact to resolve

        Returns:
            Path to artifact
        """
        curr_path: Optional[Path] = getattr(self, name)

        if curr_path is None:
            return None

        assert self.lpath is not None and self.rpath is not None

        resolved_path = self.rpath / curr_path.relative_to(self.lpath)
        return str(resolved_path)


class CardSaver:
    def __init__(self, card: Card):
        """
        Parent class for saving artifacts belonging to cards.
        ArtifactSaver controls pathing for all card objects

        Args:
            card:
                Card with artifacts to save
            card_storage_info:
                Extra info to use with artifact storage
        """

        self._card = card
        self.card_uris = CardUris()

    @cached_property
    def lpath(self) -> Path:
        assert self.card_uris.lpath is not None
        return self.card_uris.lpath

    @cached_property
    def rpath(self) -> Path:
        assert self.card_uris.rpath is not None
        return self.card_uris.rpath

    @cached_property
    def card(self) -> Card:
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

    def _save_dataset(self) -> None:
        """Logic for saving subclasses of Dataset"""
        assert isinstance(self.card.interface, Dataset), "Expected Dataset interface"
        save_path = self.lpath / SaveName.DATA.value
        self.card.interface.save_data(save_path)

        dumped_interface = self.card.interface.model_dump()

        # save dataset class to joblib
        save_path = (self.lpath / SaveName.DATASET.value).with_suffix(Suffix.JOBLIB.value)
        joblib.dump(dumped_interface, save_path)

    def _save_data_interface(self) -> None:
        """Logic for saving subclasses of DataInterface"""

        assert isinstance(self.card.interface, DataInterface), "Expected DataInterface"

        if self.card.interface.data is None:
            return

        save_path = (self.lpath / SaveName.DATA.value).with_suffix(self.card.interface.data_suffix)
        self.card.interface.save_data(save_path)

        # set feature map on metadata
        self.card.metadata.feature_map = self.card.interface.feature_map
        return

    def _save_data(self) -> None:
        """Saves a data via data interface"""

        # saving Dataset
        if isinstance(self.card.interface, Dataset):
            return self._save_dataset()

        return self._save_data_interface()

    def _save_data_profile(self) -> None:
        """Saves a data profile"""

        if isinstance(self.card.interface, Dataset):
            return

        if self.card.interface.data_profile is None:
            return

        save_path = self.lpath / SaveName.DATA_PROFILE.value

        # save html and joblib version
        self.card.interface.save_data_profile(save_path.with_suffix(Suffix.JSON.value))

    def _save_datacard(self) -> None:
        """Saves a datacard to file system"""

        exclude_attr = {"interface": {"data", "data_profile", "splits"}}

        dumped_datacard = self.card.model_dump(exclude=exclude_attr)

        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JSON.value)

        if self.card.interface.name() in [AllowedDataType.IMAGE.value, AllowedDataType.TEXT.value]:
            # remove text and image dataset interface
            dumped_datacard["interface"] = None

        # save json
        with save_path.open("w", encoding="utf-8") as file_:
            json.dump(dumped_datacard, file_)

    def save_artifacts(self) -> None:
        """Saves artifacts from a DataCard"""

        # quick checks
        if self.card.interface is None:
            raise ValueError("DataCard must have a data interface to save artifacts")

        if isinstance(self.card.interface, DataInterface):
            if self.card.interface.data is None and not bool(self.card.interface.sql_logic):
                raise ValueError("DataInterface must have data or sql logic")

        # set type needed for loading
        self.card.metadata.interface_type = self.card.interface.name()
        self.card.metadata.data_type = self.card.interface.data_type

        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_data()
            self._save_data_profile()
            self._save_datacard()
            client.storage_client.put(self.lpath, self.rpath)

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

    def _save_huggingface_preprocessor(self) -> None:
        """Saves huggingface tokenizers and feature extractors"""
        assert isinstance(self.card.interface, HuggingFaceModel), "Expected HuggingFaceModel interface"

        if self.card.interface.tokenizer is not None:
            save_path = (self.lpath / SaveName.TOKENIZER.value).with_suffix("")
            self.card.interface.save_tokenizer(save_path)
            self.card_uris.tokenizer_uri = save_path

        if self.card.interface.feature_extractor is not None:
            save_path = (self.lpath / SaveName.FEATURE_EXTRACTOR.value).with_suffix("")
            self.card.interface.save_feature_extractor(save_path)
            self.card_uris.feature_extractor_uri = save_path

    def _save_preprocessor(self) -> None:
        """Save preprocessor via model interface"""

        if isinstance(self.card.interface, HuggingFaceModel):
            return self._save_huggingface_preprocessor()

        if not hasattr(self.card.interface, "preprocessor"):
            return None

        if self.card.interface.preprocessor is not None:
            save_path = (self.lpath / SaveName.PREPROCESSOR.value).with_suffix(self.card.interface.preprocessor_suffix)
            self.card.interface.save_preprocessor(save_path)
            self.card_uris.preprocessor_uri = save_path
        return None

    def _save_sample_data(self) -> None:
        """Saves sample data associated with ModelCard to filesystem"""

        if isinstance(self.card.sample_data, DataInterface):
            save_path = (self.lpath / SaveName.SAMPLE_MODEL_DATA.value).with_suffix(self.card.sample_data.data_suffix)

        else:
            save_path = (self.lpath / SaveName.SAMPLE_MODEL_DATA.value).with_suffix(self.card.interface.data_suffix)

        self.card.interface.save_sample_data(save_path)
        self.card_uris.sample_data_uri = save_path

    def _save_onnx_config(self, onnx_args: HuggingFaceOnnxArgs) -> None:
        """Saves onnx config to file system and update path params"""

        if onnx_args.config is not None:
            save_path = (self.lpath / SaveName.ONNX_CONFIG.value).with_suffix(Suffix.JOBLIB.value)
            joblib.dump(onnx_args.config, save_path)
            self.card_uris.onnx_config_uri = save_path

        if onnx_args.quantize:
            self.card_uris.quantized_model_uri = self.lpath / SaveName.QUANTIZED_MODEL.value

    def _save_onnx_model(self) -> None:
        """If to_onnx is True, converts and saves a model to onnx format"""

        if self.card.to_onnx:
            logger.info("---------------------Converting Model to Onnx---------------------")

            save_path = (self.lpath / SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value)

            metadata = self.card.interface.save_onnx(save_path)

            if isinstance(self.card.interface, HuggingFaceModel):
                assert self.card.interface.onnx_args is not None, "onnx_args must be set for HuggingFaceModel"
                self._save_onnx_config(self.card.interface.onnx_args)

                # remove suffix for uris
                save_path = save_path.with_suffix("")

            logger.info("---------------------Onnx Conversion Complete---------------------")
        else:
            metadata = _TrainedModelMetadataCreator(self.card.interface).get_model_metadata()
            save_path = None

        self.card.metadata.data_schema = metadata.data_schema
        self.card_uris.onnx_model_uri = save_path

    def _get_model_metadata(self, existing_metadata: Dict[str, Any]) -> ModelMetadata:
        """Create Onnx Model from trained model"""
        if self.card.interface.onnx_model is not None:
            onnx_version = self.card.interface.onnx_model.onnx_version
        else:
            onnx_version = None

        # logic for drift
        drift = None

        if self.card.interface.drift_profile is not None:
            existing_drift = existing_metadata.get("drift")
            existing_drift_profile_uri = None
            existing_drift_type = None

            if existing_drift is not None:
                existing_drift_profile_uri = existing_drift.get("drift_profile_uri")
                existing_drift_type = existing_drift.get("drift_type")

            drift = {
                "drift_profile_uri": existing_drift_profile_uri
                or self.card_uris.resolve_path(UriNames.DRIFT_PROFILE_URI.value),
                "drift_type": existing_drift_type or self.card.interface.drift_profile.config.drift_type.value,
            }

        # base metadata
        metadata = ModelMetadata(
            model_name=existing_metadata.get("model_name") or self.card.name,
            model_class=existing_metadata.get("model_class") or self.card.interface.model_class,
            model_type=existing_metadata.get("model_type") or self.card.interface.model_type,
            model_interface=existing_metadata.get("model_interface") or self.card.interface.name(),
            onnx_uri=existing_metadata.get("onnx_uri") or self.card_uris.resolve_path(UriNames.ONNX_MODEL_URI.value),
            onnx_version=existing_metadata.get("onnx_version") or onnx_version,
            model_uri=existing_metadata.get("model_uri")
            or self.card_uris.resolve_path(UriNames.TRAINED_MODEL_URI.value),
            model_version=existing_metadata.get("model_version") or self.card.version,
            model_repository=existing_metadata.get("model_repository") or self.card.repository,
            data_schema=existing_metadata.get("data_schema") or self.card.metadata.data_schema,
            sample_data_uri=existing_metadata.get("sample_data_uri")
            or self.card_uris.resolve_path(UriNames.SAMPLE_DATA_URI.value),
        )

        if drift is not None:
            metadata.drift = drift

        # add extra uris
        if self.card_uris.preprocessor_uri is not None:
            metadata.preprocessor_uri = existing_metadata.get("preprocessor_uri") or self.card_uris.resolve_path(
                UriNames.PREPROCESSOR_URI.value
            )
            metadata.preprocessor_name = (
                existing_metadata.get(
                    "preprocessor_name",
                )
                or self.card.interface.preprocessor_name
            )

        # add huggingface specific uris
        if isinstance(self.card.interface, HuggingFaceModel):
            metadata.task_type = self.card.interface.task_type

            if self.card.interface.onnx_args is not None:
                metadata.onnx_args = existing_metadata.get("onnx_args") or {
                    "quantize": self.card.interface.onnx_args.quantize,
                    "ort_type": self.card.interface.onnx_args.ort_type,
                    "provider": self.card.interface.onnx_args.provider,
                }

            if self.card_uris.quantized_model_uri is not None:
                metadata.quantized_model_uri = existing_metadata.get(
                    "quantized_model_uri"
                ) or self.card_uris.resolve_path(UriNames.QUANTIZED_MODEL_URI.value)

            if self.card_uris.tokenizer_uri is not None:
                metadata.tokenizer_uri = existing_metadata.get("tokenizer_uri") or self.card_uris.resolve_path(
                    UriNames.TOKENIZER_URI.value
                )
                metadata.tokenizer_name = existing_metadata.get("tokenizer_name") or self.card.interface.tokenizer_name

            if self.card_uris.feature_extractor_uri is not None:
                metadata.feature_extractor_uri = existing_metadata.get(
                    "feature_extractor_uri"
                ) or self.card_uris.resolve_path(UriNames.FEATURE_EXTRACTOR_URI.value)
                metadata.feature_extractor_name = (
                    existing_metadata.get("feature_extractor_name") or self.card.interface.feature_extractor_name
                )

            if self.card_uris.onnx_config_uri is not None:
                metadata.onnx_config_uri = existing_metadata.get("onnx_config_uri") or self.card_uris.resolve_path(
                    UriNames.ONNX_CONFIG_URI.value
                )

        return metadata

    def _save_metadata(self) -> None:
        """Saves Model metadata"""

        # check if model metadata already exists (for updating cards)
        existing_metadata = {}
        exists = client.storage_client.exists(
            (self.rpath / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
        )

        if exists:
            existing_path = Path(self.rpath / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
            local_path = Path(self.lpath / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
            client.storage_client.get(existing_path, local_path)

            # load json
            existing_metadata = ModelMetadata.model_validate_json(
                local_path.read_text("utf-8"),
            ).model_dump()

        model_metadata = self._get_model_metadata(existing_metadata)

        # save model metadata to json
        save_path = Path(self.lpath / SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
        save_path.write_text(model_metadata.model_dump_json(), "utf-8")

    def _save_modelcard(self) -> None:
        """Saves a modelcard to file system"""

        dumped_model = self.card.model_dump(
            exclude={
                "interface": {
                    "model",
                    "preprocessor",
                    "sample_data",
                    "onnx_model",
                    "feature_extractor",
                    "tokenizer",
                    "drift_profile",
                },
            }
        )
        if dumped_model["interface"].get("onnx_args") is not None:
            if dumped_model["interface"]["onnx_args"].get("config") is not None:
                dumped_model["interface"]["onnx_args"].pop("config")

        keys = [*dumped_model.keys(), *dumped_model["interface"].keys()]
        schema = ModelCardSchema.get_schema()

        assert set(keys).issubset(schema), f"Keys: {keys} not subset of schema: {schema}"
        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JSON.value)

        # save json
        with save_path.open("w", encoding="utf-8") as file_:
            json.dump(dumped_model, file_)

    def _save_drift_profile(self) -> None:
        """Saves drift profile to file system"""

        if self.card.interface.drift_profile is None:
            return

        assert self.card.interface.drift_profile is not None, "Drift Profile must be set on Model Interface"

        # update config with model name, repository and version
        self.card.interface.drift_profile.update_config_args(
            name=self.card.name,
            repository=self.card.repository,
            version=self.card.version,
        )

        # update drift profile repository, name and version
        save_path = Path(self.lpath / SaveName.DRIFT_PROFILE.value).with_suffix(Suffix.JSON.value)
        self.card.interface.save_drift_profile(save_path)
        self.card_uris.drift_profile_uri = save_path

    def save_artifacts(self) -> None:
        """Prepares and saves artifacts from a modelcard"""
        if self.card.interface is None:
            raise ValueError("ModelCard must have a model interface to save artifacts")

        # set type needed for loading
        self.card.metadata.interface_type = self.card.interface.__class__.__name__
        self.card.interface.modelcard_uid = str(self.card.uid)

        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri

            self._save_drift_profile()
            self._save_model()
            self._save_preprocessor()
            self._save_onnx_model()
            self._save_sample_data()
            self._save_modelcard()
            self._save_metadata()

            client.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type


class AuditCardSaver(CardSaver):
    @cached_property
    def card(self) -> AuditCard:
        return cast(AuditCard, self._card)

    def _save_auditcard(self) -> None:
        """Save auditcard to file"""
        dumped_audit = self.card.model_dump()
        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JSON.value)

        # save json
        with save_path.open("w", encoding="utf-8") as file_:
            json.dump(dumped_audit, file_)

    def save_artifacts(self) -> None:
        """Save auditcard artifacts"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_auditcard()
            client.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.AUDITCARD.value in card_type


class RunCardSaver(CardSaver):
    @cached_property
    def card(self) -> RunCard:
        return cast(RunCard, self._card)

    def _save_runcard(self) -> None:
        """Saves a runcard"""

        dumped_run = self.card.model_dump(exclude={"metrics"})  # metrics are recorded to db
        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JSON.value)

        # save json
        with save_path.open("w", encoding="utf-8") as file_:
            json.dump(dumped_run, file_)

    def save_artifacts(self) -> None:
        """Saves a runcard's artifacts"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_runcard()
            client.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.RUNCARD.value in card_type


class PipelineCardSaver(CardSaver):
    @cached_property
    def card(self) -> PipelineCard:
        return cast(PipelineCard, self._card)

    def _save_pipelinecard(self) -> None:
        """Saves a pipelinecard"""
        dumped_pipeline = self.card.model_dump()
        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JSON.value)

        # save json
        with save_path.open("w", encoding="utf-8") as file_:
            json.dump(dumped_pipeline, file_)

    def save_artifacts(self) -> None:
        """Saves a pipelinecard's artifacts"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_pipelinecard()
            client.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.PIPELINECARD.value in card_type


class ProjectCardSaver(CardSaver):
    @cached_property
    def card(self) -> ProjectCard:
        return cast(ProjectCard, self._card)

    def _save_projectcard(self) -> None:
        """Saves a projectcard"""
        dumped_project = self.card.model_dump()
        save_path = Path(self.lpath / SaveName.CARD.value).with_suffix(Suffix.JSON.value)

        # save json
        with save_path.open("w", encoding="utf-8") as file_:
            json.dump(dumped_project, file_)

    def save_artifacts(self) -> None:
        """Saves a projectcard's artifacts"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.card_uris.lpath = Path(tmp_dir)
            self.card_uris.rpath = self.card.uri
            self._save_projectcard()
            client.storage_client.put(self.lpath, self.rpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.PROJECTCARD.value in card_type


def save_card_artifacts(card: Card) -> None:
    """Saves a given Card's artifacts to a filesystem

    Args:
        card:
            Card to save

    Returns:
        Card with updated artifact uris

    """

    card_saver = next(
        card_saver for card_saver in CardSaver.__subclasses__() if card_saver.validate(card_type=card.card_type)
    )

    saver = card_saver(card=card)

    return saver.save_artifacts()
