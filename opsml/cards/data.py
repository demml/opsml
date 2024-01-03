# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# IMPORTANT: We need `Optional` imported here in order for Pydantic to be able to
# deserialize DataCard.
#
from typing import (  # noqa # pylint: disable=unused-import
    Any,
    Dict,
    List,
    Optional,
    Union,
)

from pydantic import SerializeAsAny

from opsml.cards.base import ArtifactCard
from opsml.data.interfaces import DataInterface
from opsml.data.splitter import DataHolder, DataSplit
from opsml.helpers.logging import ArtifactLogger
from opsml.types import CardType, DataCardMetadata

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

    def load_data(self):
        """
        Load data to interface
        """
        from opsml.cards.card_loader import DataCardLoader

        DataCardLoader(self).load_data()

    def load_data_profile(self):
        """
        Load data to interface
        """
        from opsml.cards.card_loader import DataCardLoader

        DataCardLoader(self).load_data_profile()

    def create_registry_record(self) -> Dict[str, Any]:
        """
        Creates required metadata for registering the current data card.
        Implemented with a DataRegistry object.
            Returns:
            Registry metadata
        """
        exclude_attr = {"data"}
        return self.model_dump(exclude=exclude_attr)

    def add_info(self, info: Dict[str, Union[float, int, str]]) -> None:
        """
        Adds metadata to the existing DataCard metadata dictionary

        Args:
            info:
                Dictionary containing name (str) and value (float, int, str) pairs
                to add to the current metadata set
        """

        self.metadata.additional_info = {**info, **self.metadata.additional_info}

    def split_data(self) -> DataHolder:
        """Splits data interface according to data split logic"""
        return self.interface.split_data()

    @property
    def data_splits(self) -> List[DataSplit]:
        """Returns data splits"""
        return self.interface.data_splits

    @property
    def data(self) -> Any:
        """Returns data"""
        return self.interface.data

    @property
    def card_type(self) -> str:
        return CardType.DATACARD.value
