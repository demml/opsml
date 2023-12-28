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

logger = ArtifactLogger.get_logger()


class DataCard(ArtifactCard):
    """Create a DataCard from your data.

    Args:
        data:
            Data to use for data card. Can be a pyarrow table, pandas dataframe, polars dataframe
            or numpy array
        name:
            What to name the data
        team:
            Team that this data is associated with
        user_email:
            Email to associate with data card
        dependent_vars:
            List of dependent variables. Can be string or index if using numpy
        data_splits:
            Optional list of `DataSplit`
        sql_logic:
            Dictionary of strings containing sql logic or sql files used to create the data
        version:
            DataCard version
        uid:
            Unique id assigned to the DataCard
        data_profile:
            Optional ydata-profiling `ProfileReport`

    Returns:
        DataCard

    """

    interface: SerializeAsAny[DataInterface] = None
    metadata: DataCardMetadata = DataCardMetadata()

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
