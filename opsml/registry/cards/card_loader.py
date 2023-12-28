# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import tempfile
from functools import cached_property
from pathlib import Path
from typing import Any, Optional, Tuple, cast

import joblib
from pydantic import BaseModel

from opsml.registry.cards.audit import AuditCard
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.data import DataCard
from opsml.registry.cards.model import ModelCard
from opsml.registry.cards.pipeline import PipelineCard
from opsml.registry.cards.project import ProjectCard
from opsml.registry.cards.run import RunCard
from opsml.registry.model.metadata_creator import _TrainedModelMetadataCreator
from opsml.registry.storage import client
from opsml.registry.types import CardType, ModelMetadata, SaveName, UriNames
from opsml.registry.types.extra import Suffix


class CardLoader:
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
        self.storage_client = client.storage_client

    @cached_property
    def card(self) -> ArtifactCard:
        return self.card

    @cached_property
    def storage_suffix(self) -> str:
        return self.card.interface.storage_suffix

    def _load_object(self, object_path: str, suffix: str) -> Path:
        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri

            load_lpath = Path(lpath, object_path).with_suffix(suffix)
            load_rpath = Path(rpath, object_path).with_suffix(suffix)

            self.storage_client.get(load_rpath, load_lpath)

            return load_lpath

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardLoader(CardLoader):
    """DataCard loader. Methods are meant to be called individually"""

    @cached_property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def load_data(self) -> None:
        """Saves a data via data interface"""

        if self.card.interface.data is not None:
            return None

        lpath = self._load_object(SaveName.DATA.value, self.storage_suffix)
        self.card.interface.load_data(lpath)

    def load_data_profile(self) -> None:
        """Saves a data profile"""

        # check exists
        rpath = Path(self.card.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JOBLIB.value)
        if not self.storage_client.exists(rpath):
            return None

        # load data profile
        lpath = self._load_object(SaveName.DATA_PROFILE.value, Suffix.JOBLIB.value)
        self.card.interface.load_profile(lpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelCardLoader(CardLoader):
    """ModelCard loader. Methods are meant to be called individually"""

    @cached_property
    def card(self) -> ModelCard:
        return cast(ModelCard, self._card)

    def load_sample_data(self) -> None:
        pass

    def load_preprocessor(self) -> None:
        pass

    def load_model(self) -> None:
        """Saves a data via data interface"""

        if self.card.interface.model is not None:
            return None

        lpath = self._load_object(SaveName.TRAINED_MODEL, self.storage_suffix)
        self.card.interface.load_data(lpath)

    def load_data_profile(self) -> None:
        """Saves a data profile"""

        # check exists
        rpath = Path(self.card.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JOBLIB.value)
        if not self.storage_client.exists(rpath):
            return None

        # load data profile
        lpath = self._load_object(SaveName.DATA_PROFILE.value, Suffix.JOBLIB.value)
        self.card.interface.load_profile(lpath)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type
