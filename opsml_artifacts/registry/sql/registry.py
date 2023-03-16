from typing import Any, Dict, Iterable, List, Optional, Union, cast

import pandas as pd
from sqlalchemy.sql.expression import ColumnElement, FromClause

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.cards import (
    DataCard,
    ExperimentCard,
    ModelCard,
    PipelineCard,
)
from opsml_artifacts.registry.cards.types import ArtifactCardProto
from opsml_artifacts.registry.sql.records import (
    DataRegistryRecord,
    ExperimentRegistryRecord,
    ModelRegistryRecord,
    PipelineRegistryRecord,
)
from opsml_artifacts.registry.sql.registry_base import Registry, SQLRegistryBase
from opsml_artifacts.registry.sql.sql_schema import RegistryTableNames

logger = ArtifactLogger.get_logger(__name__)


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]
CardTypes = Union[ExperimentCard, ModelCard, DataCard, PipelineCard]


class DataCardRegistry(Registry):

    # specific update logic
    def update_card(self, card: DataCard) -> None:

        """Updates an existing data card in the data registry

        Args:
            data_card (DataCard): Existing data card record

        Returns:
            None
        """

        record = DataRegistryRecord(**card.dict())
        self._update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.DATA


class ModelCardRegistry(Registry):
    def update_card(self, card: ModelCard) -> None:

        """Updates an existing model card

        Args:
            model_card (ModelCard): Existing model card record

        Returns:
            None
        """

        record = ModelRegistryRecord(**card.dict())
        self._update_record(record=record.dict())

    def _get_data_table_name(self) -> str:
        return RegistryTableNames.DATA.value

    def _validate_datacard_uid(self, uid: str) -> None:
        table_to_check = self._get_data_table_name()
        exists = self._check_uid(uid=uid, table_to_check=table_to_check)
        if not exists:
            raise ValueError("""ModelCard must be assoicated with a valid DataCard uid""")

    def _has_data_card_uid(self, uid: Optional[str]) -> bool:
        return bool(uid)

    # custom registration
    def register_card(
        self,
        card: ArtifactCardProto,
        version_type: str = "minor",
        save_path: Optional[str] = None,
    ) -> None:
        """
        Adds new record to registry.

        Args:
            Card (ArtifactCard): Card to register
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
            save_path (str): Blob path to save card artifacts too.
            This path SHOULD NOT include the base prefix (e.g. "gs://my_bucket")
            - this prefix is already inferred using either "OPSML_TRACKING_URI" or "OPSML_STORAGE_URI"
            env variables. In addition, save_path should specify a directory.
        """

        model_card = cast(ModelCard, card)

        if not self._has_data_card_uid(uid=model_card.data_card_uid):
            raise ValueError("""ModelCard must be associated with a valid DataCard uid""")

        if model_card.data_card_uid is not None:
            self._validate_datacard_uid(uid=model_card.data_card_uid)

        return super().register_card(
            card=card,
            version_type=version_type,
            save_path=save_path,
        )

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.MODEL


class ExperimentCardRegistry(Registry):
    def update_card(self, card: ExperimentCard) -> None:

        """Updates an existing pipeline card in the pipeline registry

        Args:
            card (PipelineCard): Existing pipeline card

        Returns:
            None
        """

        record = ExperimentRegistryRecord(**card.dict())
        self._update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.EXPERIMENT


class PipelineCardRegistry(Registry):
    def update_card(self, card: PipelineCard) -> None:

        """Updates an existing pipeline card in the pipeline registry

        Args:
            card (PipelineCard): Existing pipeline card

        Returns:
            None
        """

        record = PipelineRegistryRecord(**card.dict())
        self._update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.PIPELINE


# CardRegistry also needs to set a storage file system
class CardRegistry:
    def __init__(self, registry_name: str):

        """Interface for connecting to any of the ArtifactCard registries

        Args:
            registry_name (str): Name of the registry to connect to. Options are
            "pipeline", "model", "data" and "experiment".

        Returns:
            Instantiated connection to specific Card registry

        Example:

            # With connection type
            cloud_sql = CloudSQLConnection(...)
            data_registry = CardRegistry(registry_name="data", connection_client=cloud_sql)

            # With connection client
            data_registry = CardRegistry(registry_name="data", connection_type="gcp")

        """

        self.registry: SQLRegistryBase = self._set_registry(registry_name=registry_name)
        self.table_name = self.registry._table.__tablename__

    def _set_registry(self, registry_name: str) -> Registry:

        """Returns a SQL registry to be used to register Cards

        Args:
            registry_name (str): Name of the registry (pipeline, model, data, experiment)

        Returns:
            SQL Registry
        """

        registry_name = RegistryTableNames[registry_name.upper()].value
        registry = next(
            registry
            for registry in Registry.__subclasses__()
            if registry.validate(
                registry_name=registry_name,
            )
        )

        return registry(table_name=registry_name)

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
    ) -> pd.DataFrame:

        """Retrieves records from registry

        Args:
            name (str): Card name
            team (str): Team associated with card
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for Card. If present, the uid takes precedence.


        Returns:
            pandas dataframe of records
        """

        if name is not None:
            name = name.lower()

        if team is not None:
            team = team.lower()

        card_list = self.registry.list_cards(uid=uid, name=name, team=team, version=version)
        return pd.DataFrame(card_list)

    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        uid: Optional[str] = None,
        version: Optional[str] = None,
    ) -> CardTypes:

        """Loads a specific card

        Args:
            name (str): Optional Card name
            team (str): Optional team associated with card
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.

        Returns
            ArtifactCard
        """
        if name is not None:
            name = name.lower()
            name = name.replace("_", "-")

        if team is not None:
            team = team.lower()

        return self.registry.load_card(uid=uid, name=name, team=team, version=version)

    def register_card(
        self,
        card: ArtifactCardProto,
        version_type: str = "minor",
        save_path: Optional[str] = None,
    ) -> None:
        """
        Adds new record to registry.

        Args:
            Card (ArtifactCard): Card to register
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
            save_path (str): Blob path to save card artifacts too.
            This path SHOULD NOT include the base prefix (e.g. "gs://my_bucket")
            - this prefix is already inferred using either "OPSML_TRACKING_URI" or "OPSML_STORAGE_URI"
            env variables. In addition, save_path should specify a directory.
        """

        self.registry.register_card(
            card=card,
            version_type=version_type,
            save_path=save_path,
        )

    def update_card(
        self,
        card: CardTypes,
    ) -> None:
        """Update and artifact card (DataCard only) based on current registry

        Args:
            card (DataCard or ModelCard): Card to register

        Returns:
            None
        """

        if not hasattr(self.registry, "update_card"):
            raise ValueError(f"""{card.__class__.__name__} has no 'update_card' attribute""")

        self.registry = cast(DataCardRegistry, self.registry)
        card = cast(DataCard, card)
        return self.registry.update_card(card=card)

    def query_value_from_card(self, uid: str, columns: List[str]) -> Dict[str, Any]:
        """Query column values from a specific Card

        Args:
            uid (str): Uid of Card
            columns (List[str]): List of columns to query

        Returns:
            Dictionary of column, values pairs
        """
        results = self.registry.list_cards(uid=uid)[0]  # pylint: disable=protected-access
        return {col: results[col] for col in columns}
