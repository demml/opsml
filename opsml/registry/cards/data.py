# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Union

from pydantic import SerializeAsAny

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.data.interfaces import DataInterface
from opsml.registry.sql.records import DataRegistryRecord, RegistryRecord
from opsml.registry.types import CardType, DataCardMetadata
from opsml.registry.cards.card_loader import DataCardLoader

logger = ArtifactLogger.get_logger()


class DataCard(ArtifactCard):
    """Create a DataCard from your data.

    Args:
        interface:
            Instance of `DataInterface` that contains data
        name:
            What to name the data
        team:
            Team that this data is associated with
        user_email:
            Email to associate with data card
        version:
            DataCard version
        uid:
            Unique id assigned to the DataCard

    Returns:
        DataCard

    """

    interface: SerializeAsAny[DataInterface]
    metadata: DataCardMetadata = DataCardMetadata()

    def load_model(self):
        """
        Load data to interface
        """
        DataCardLoader(self).load_data()

    def load_data_profile(self):
        """
        Load data to interface
        """
        DataCardLoader(self).load_data_profile()

    def create_registry_record(self, **kwargs: Dict[str, Any]) -> RegistryRecord:
        """
        Creates required metadata for registering the current data card.
        Implemented with a DataRegistry object.

        Returns:
            Registry metadata

        """
        exclude_attr = {"data"}
        return DataRegistryRecord(**{**self.model_dump(exclude=exclude_attr), **kwargs})

    def add_info(self, info: Dict[str, Union[float, int, str]]) -> None:
        """
        Adds metadata to the existing DataCard metadata dictionary

        Args:
            info:
                Dictionary containing name (str) and value (float, int, str) pairs
                to add to the current metadata set
        """

        self.metadata.additional_info = {**info, **self.metadata.additional_info}

    @property
    def card_type(self) -> str:
        return CardType.DATACARD.value
