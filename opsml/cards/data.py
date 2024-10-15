# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
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

from pydantic import ConfigDict, SerializeAsAny
from scouter import DataProfile

from opsml.cards.base import ArtifactCard
from opsml.data import Dataset
from opsml.data.interfaces._base import DataInterface
from opsml.data.splitter import Data, DataSplit
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
        repository:
            Repository that this data is associated with
        contact:
            Contact to associate with data card
        info:
            `CardInfo` object containing additional metadata. If provided, it will override any
            values provided for `name`, `repository`, `contact`, and `version`.

            Name, repository, and contact are required arguments for all cards. They can be provided
            directly or through a `CardInfo` object.

        version:
            DataCard version
        uid:
            Unique id assigned to the DataCard

    Returns:
        DataCard

    """

    model_config = ConfigDict(extra="forbid")

    interface: SerializeAsAny[Union[DataInterface, Dataset]]
    metadata: DataCardMetadata = DataCardMetadata()

    def load_data(self, **kwargs: Union[str, int]) -> None:  # pylint: disable=differing-param-doc
        """
        Load data to interface

        Args:
            kwargs:
                Keyword arguments to pass to the data loader

            ---- Supported kwargs for ImageData and TextDataset ----

            split:
                Split to use for data. If not provided, then all data will be loaded.
                Only used for subclasses of `Dataset`.

            batch_size:
                What batch size to use when loading data. Only used for subclasses of `Dataset`.
                Defaults to 1000.

            chunk_size:
                How many files per batch to use when writing arrow back to local file.
                Defaults to 1000.

                Example:

                    - If batch_size=1000 and chunk_size=100, then the loaded batch will be split into
                    10 chunks to write in parallel. This is useful for large datasets.

        """
        from opsml.storage.card_loader import DataCardLoader

        DataCardLoader(self).load_data(**kwargs)

    def create_data_profile(self, bin_size: int = 20) -> Optional[DataProfile]:
        """
        Create data profile for the current data card

        Args:
            bin_size:
                Number of bins for histograms. Default is 20
        """
        if isinstance(self.interface, DataInterface):
            return self.interface.create_data_profile(bin_size=bin_size)

        logger.warning("Data profile is only supported for DataInterface subclasses. You have a Dataset subclass.")
        return None

    def load_data_profile(self) -> None:
        """
        Load data to interface
        """
        from opsml.storage.card_loader import DataCardLoader

        DataCardLoader(self).load_data_profile()

    def create_registry_record(self) -> Dict[str, Any]:
        """
        Creates required metadata for registering the current data card.
        Implemented with a DataRegistry object.
            Returns:
            Registry metadata
        """
        exclude_attr = {"data"}
        dumped_model = self.model_dump(exclude=exclude_attr)
        dumped_model["interface_type"] = self.interface.name()
        return dumped_model

    def add_info(self, info: Dict[str, Union[float, int, str]]) -> None:
        """
        Adds metadata to the existing DataCard metadata dictionary

        Args:
            info:
                Dictionary containing name (str) and value (float, int, str) pairs
                to add to the current metadata set
        """

        self.metadata.additional_info = {**info, **self.metadata.additional_info}

    def split_data(self) -> Dict[str, Data]:
        """Splits data interface according to data split logic"""

        assert isinstance(self.interface, DataInterface), "Splitting is only support for DataInterface subclasses"
        if self.data is None:
            self.load_data()

        return self.interface.split_data()

    @property
    def data_splits(self) -> List[DataSplit]:
        """Returns data splits"""
        assert isinstance(self.interface, DataInterface), "Data splits are only supported for DataInterface subclasses"
        return self.interface.data_splits

    @property
    def data(self) -> Any:
        """Returns data"""
        assert isinstance(self.interface, DataInterface), "Data attribute is only supported for DataInterface subclasses"
        return self.interface.data

    @property
    def data_profile(self) -> Any:
        """Returns data profile"""
        assert isinstance(self.interface, DataInterface), "Data profile is only supported for DataInterface subclasses"
        return self.interface.data_profile

    @property
    def card_type(self) -> str:
        return CardType.DATACARD.value
