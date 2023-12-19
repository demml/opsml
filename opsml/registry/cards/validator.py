# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Optional

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.types import (
    AllowedDataType,
    DataCardMetadata,
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
        self.metadata = metadata
        self.sql_logic = sql_logic

    @property
    def has_data_uri(self) -> bool:
        """Checks if data uri is present in metadata"""
        if self.metadata is not None:
            return bool(self.check_metadata())
        return False

    def get_data_type(self) -> str:
        """Get data allowed datatype for DataCard"""
        if self.data is None and bool(self.sql_logic):
            return AllowedDataType.SQL
        return check_data_type(self.data)

    def check_metadata(self) -> Optional[str]:
        """Validates metadata

        Returns:
            Data uri if present
        """

        if isinstance(self.metadata, DataCardMetadata):
            data_uri = self.metadata.uris.data_uri
        else:
            assert isinstance(self.metadata, dict)
            data_uri = self.metadata["uris"].get("data_uri")

        if self.data is None and not bool(self.sql_logic):
            if data_uri is None:
                raise ValueError("Data or sql logic must be supplied when no data_uri is present")
        return data_uri

    def get_metadata(self) -> DataCardMetadata:
        """Get metadata for DataCard

        Returns:
            `DataCardMetadata` with updated data_type
        """
        data_type = self.get_data_type()
        if self.metadata is None:
            self.metadata = DataCardMetadata(data_type=data_type)

        elif isinstance(self.metadata, DataCardMetadata):
            self.metadata.data_type = data_type

        elif isinstance(self.metadata, dict):
            self.metadata["data_type"] = data_type

        return self.metadata
