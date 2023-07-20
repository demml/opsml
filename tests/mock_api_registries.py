import os
from typing import Any, Dict, Iterable, List, Optional, Union, cast
import pandas as pd
from sqlalchemy.sql.expression import ColumnElement, FromClause
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.cards import (
    ArtifactCard,
    DataCard,
    RunCard,
    ModelCard,
    PipelineCard,
)
from opsml.registry.sql.records import (
    DataRegistryRecord,
    RunRegistryRecord,
    PipelineRegistryRecord,
    ModelRegistryRecord,
)
from opsml.registry.cards.types import CardInfo, CardType
from opsml.registry.sql.registry_base import ClientRegistry, SQLRegistryBase, VersionType
from opsml.registry.sql.sql_schema import RegistryTableNames

logger = ArtifactLogger.get_logger(__name__)


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]


# Separate module to force use of ClientRegistry for some tests
Registry = ClientRegistry


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
        self.update_card_record(card=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.DATA.value


class ModelCardRegistry(Registry):
    def _get_data_table_name(self) -> str:
        return RegistryTableNames.DATA.value

    def _validate_datacard_uid(self, uid: str) -> None:
        table_to_check = self._get_data_table_name()
        exists = self.check_uid(uid=uid, table_to_check=table_to_check)
        if not exists:
            raise ValueError("""ModelCard must be assoicated with a valid DataCard uid""")

    def _has_datacard_uid(self, uid: Optional[str]) -> bool:
        return bool(uid)

    # custom registration
    def register_card(
        self,
        card: ArtifactCard,
        version_type: VersionType = VersionType.MINOR,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Adds new record to registry.

        Args:
            card:
                card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor"
            save_path:
                Blob path to save card artifacts too. This path SHOULD NOT
                include the base prefix (e.g. "gs://my_bucket" - this prefix is
                already inferred using either "OPSML_TRACKING_URI" or
                "OPSML_STORAGE_URI" env variables. In addition, save_path should
                specify a directory.
        """

        model_card = cast(ModelCard, card)

        if not self._has_datacard_uid(uid=model_card.datacard_uid):
            raise ValueError("""ModelCard must be associated with a valid DataCard uid""")

        if model_card.datacard_uid is not None:
            self._validate_datacard_uid(uid=model_card.datacard_uid)

        return super().register_card(
            card=card,
            version_type=version_type,
            save_path=save_path,
        )

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.MODEL.value


class RunCardRegistry(Registry):  # type:ignore
    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.RUN.value


class PipelineCardRegistry(Registry):  # type:ignore
    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.PIPELINE.value


class ProjectCardRegistry(Registry):  # type:ignore
    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.PROJECT.value


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

        self._registry: SQLRegistryBase = self._set_registry(registry_name=registry_name)
        self.table_name = self._registry._table.__tablename__

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
        tags: Optional[Dict[str, str]] = None,
        info: Optional[CardInfo] = None,
        max_date: Optional[str] = None,
        limit: Optional[int] = None,
        as_dataframe: bool = True,
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """Retrieves records from registry

        Args:
            name:
                Card name
            team:
                Team associated with card
            version:
                Optional version number of existing data. If not specified, the
                most recent version will be used
            tags:
                Dictionary of key, value tags to search for
            uid:
                Unique identifier for Card. If present, the uid takes precedence
            max_date:
                Max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01")
            limit:
                Places a limit on result list. Results are sorted by SemVer

        Returns:
            pandas dataframe of records or list of dictionaries
        """

        if info is not None:
            name = name or info.name
            team = team or info.team
            uid = uid or info.uid
            version = version or info.version
            tags = tags or info.tags

        if name is not None:
            name = name.lower()

        if team is not None:
            team = team.lower()

        card_list = self._registry.list_cards(
            uid=uid,
            name=name,
            team=team,
            version=version,
            max_date=max_date,
            limit=limit,
            tags=tags,
        )

        if as_dataframe:
            return pd.DataFrame(card_list)

        return card_list

    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        uid: Optional[str] = None,
        version: Optional[str] = None,
    ) -> ArtifactCard:
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

        return self._registry.load_card(uid=uid, name=name, team=team, version=version)

    def register_card(
        self,
        card: ArtifactCard,
        version_type: VersionType = VersionType.MINOR,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Adds new record to registry.

        Args:
            card:
                Card to register
            version_type:
                Version type for increment. Options are "major", "minor" and "patch". Defaults to "minor"
            save_path:
                Blob path to save card artifacts too. This path SHOULD NOT
                include the base prefix (e.g. "gs://my_bucket") - this prefix is
                already inferred using either "OPSML_TRACKING_URI" or
                "OPSML_STORAGE_URI" env variables. In addition, save_path should
                specify a directory.
        """

        self._registry.register_card(
            card=card,
            version_type=version_type,
            save_path=save_path,
        )

    def update_card(
        self,
        card: ArtifactCard,
    ) -> None:
        """Update and artifact card (DataCard only) based on current registry

        Args:
            card (DataCard or ModelCard): Card to register

        Returns:
            None
        """

        return self._registry.update_card(card=card)

    def query_value_from_card(self, uid: str, columns: List[str]) -> Dict[str, Any]:
        """Query column values from a specific Card

        Args:
            uid (str): Uid of Card
            columns (List[str]): List of columns to query

        Returns:
            Dictionary of column, values pairs
        """
        results = self._registry.list_cards(uid=uid)[0]  # pylint: disable=protected-access
        return {col: results[col] for col in columns}
