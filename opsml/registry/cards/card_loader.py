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

    def save_artifacts(self) -> Tuple[Any, Any]:
        raise NotImplementedError

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardLoader(CardLoader):
    @cached_property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def load_data(self) -> None:
        """Saves a data via data interface"""

        if self.card.interface.data is not None:
            return None

        with tempfile.TemporaryDirectory() as tmp_dir:
            lpath = Path(tmp_dir)
            rpath = self.card.uri

            load_rpath = self.rpath / SaveName.DATA.value

            self.storage_client.get(lpath, rpath)

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

        # quick checks
        if self.card.interface is None:
            raise ValueError("DataCard must have a data interface to save artifacts")

        if self.card.interface.data is None and bool(self.card.interface.sql_logic) is None:
            raise ValueError("DataInterface must have data or sql logic")

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
