from pathlib import Path
from typing import Optional, cast

import pandas as pd
from opsml import CardRegistry, DataCard, RegistryType
from opsml.data import (
    DataInterface,
    DataInterfaceMetadata,
    DataInterfaceSaveMetadata,
    DataLoadKwargs,
    DataSaveKwargs,
)
from opsml.helpers.data import create_fake_data

"""This example demonstrates how to save a pandas dataframe with a custom save method
"""


class CustomData(DataInterface):
    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> DataInterfaceMetadata:
        # Custom save logic here
        data_path = Path("custom_data.parquet")
        save_path = path / data_path

        data = cast(pd.DataFrame, self.data)
        data.to_parquet(save_path, index=False)

        metadata = DataInterfaceSaveMetadata(
            data_uri=data_path,
        )

        return DataInterfaceMetadata(
            save_metadata=metadata,
            schema=self.schema,
            extra_metadata={},
            sql_logic=self.sql_logic,
            interface_type=self.interface_type,
            data_splits=self.data_splits,
            dependent_vars=self.dependent_vars,
            data_type=self.data_type,
        )

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        # Custom load logic here
        load_path = path / metadata.data_uri
        data = pd.read_parquet(load_path)
        self.data = data

        return None

    @staticmethod
    def from_metadata(metadata: DataInterfaceMetadata) -> "CustomData":
        """Load interface from metadata. This is only used to instantiate the class.

        Args:
            metadata (DataInterfaceMetadata):
                Metadata to load the data from.

        """

        return CustomData(data=None)


registry = CardRegistry(RegistryType.Data)

data, _ = create_fake_data(n_samples=1200, n_categorical_features=2)


interface = CustomData(data=data)

card = DataCard(
    interface=interface,
    space="opsml",
    name="custom_data",
)

registry.register_card(card=card)
registry.list_cards().as_table()

loaded_card: DataCard = registry.load_card(uid=card.uid, interface=CustomData)

loaded_card.load()

assert isinstance(loaded_card.data, pd.DataFrame)
