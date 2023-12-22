# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Optional

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.types import (
    AllowedDataType,
    DataCardMetadata,
    UriNames,
    ValidData,
    check_data_type,
)

logger = ArtifactLogger.get_logger()


class CardValidator:
    """Base class for card validators to be used during card instantiation"""

    def get_metadata(self) -> Any:
        raise NotImplementedError


class DataCardValidator(CardValidator):
    def __init__(
        self,
        data: ValidData,
        sql_logic: Dict[str, str],
        uris: Dict[str, str],
        metadata: Optional[DataCardMetadata] = None,
    ) -> None:
        """DataCardValidator validator to be used during DataCard instantiation

        Args:
            data:
                Data to be used for DataCard
            sql_logic:
                SQL logic to be used for DataCard
            metadata:
                Metadata to be used for DataCard
        """
        self.data = data
        self.sql_logic = sql_logic
        self.uris = uris
        self.metadata = metadata

    @property
    def has_datacard_uri(self) -> bool:
        """Checks if data uri is present in metadata"""
        if self.uris is not None:
            return bool(self.uris.get(UriNames.DATACARD_URI))
        return False

    def get_data_type(self) -> str:
        """Get data allowed datatype for DataCard"""
        if self.data is None and bool(self.sql_logic):
            return AllowedDataType.SQL
        return check_data_type(self.data)

    def check_uris(self) -> Optional[str]:
        """Validates metadata

        Returns:
            Data uri if present
        """
        data_uri = None
        if self.uris is not None:
            data_uri = self.uris.get(UriNames.DATACARD_URI)

        if self.data is None and not bool(self.sql_logic):
            if data_uri is None:
                raise ValueError("Data or sql logic must be supplied when no data_uri is present")

    def get_metadata(self) -> DataCardMetadata:
        """Get metadata for DataCard

        Returns:
            `DataCardMetadata` with updated data_type
        """

        self.check_uris()
        data_type = self.get_data_type()
        if self.metadata is None:
            self.metadata = DataCardMetadata(data_type=data_type)

        elif isinstance(self.metadata, DataCardMetadata):
            self.metadata.data_type = data_type

        elif isinstance(self.metadata, dict):
            self.metadata["data_type"] = data_type

        return self.metadata
