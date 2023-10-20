# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Iterable, List, Optional, Union, cast, TYPE_CHECKING
import textwrap
import pandas as pd
from sqlalchemy.sql.expression import ColumnElement, FromClause
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards import ArtifactCard, ModelCard
from opsml.registry.cards.types import CardInfo, CardType
from opsml.registry.sql.semver import VersionType
from opsml.registry.sql.base.server import ServerRegistry
from opsml.registry.sql.base import OpsmlRegistry
from opsml.registry.sql.sql_schema import RegistryTableNames
from opsml.registry.storage.storage_system import StorageClientType


logger = ArtifactLogger.get_logger()


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]


if TYPE_CHECKING:
    Registry = ServerRegistry
else:
    Registry = OpsmlRegistry


class DataCardRegistry(Registry):
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
            raise ValueError("ModelCard must be associated with a valid DataCard uid")

    def _has_datacard_uid(self, uid: Optional[str]) -> bool:
        return bool(uid)

    def register_card(
        self,
        card: ArtifactCard,
        version_type: VersionType = VersionType.MINOR,
        pre_tag: str = "rc",
        build_tag: str = "build",
    ) -> None:
        """
        Adds new record to registry.

        Args:
            card:
                Card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor"
            pre_tag:
                pre-release tag
            build_tag:
                build tag
        """

        if card.uid is not None:
            logger.info(
                textwrap.dedent(
                    f"""
                Card {card.uid} already exists. Skipping registration. If you'd like to register 
                a new card, please instantiate a new Card object. If you'd like to update the 
                existing card, please use the update_card method.
                """
                )
            )

        else:
            model_card = cast(ModelCard, card)

            if not self._has_datacard_uid(uid=model_card.datacard_uid):
                raise ValueError("""ModelCard must be associated with a valid DataCard uid""")

            if model_card.datacard_uid is not None:
                self._validate_datacard_uid(uid=model_card.datacard_uid)

            super().register_card(
                card=card,
                version_type=version_type,
                pre_tag=pre_tag,
                build_tag=build_tag,
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

    def delete_card(self, card: ArtifactCard) -> None:
        raise ValueError("PipelineCardRegistry does not support delete_card")


class ProjectCardRegistry(Registry):  # type:ignore
    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.PROJECT.value

    def load_card(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        uid: Optional[str] = None,
        ignore_release_candidates: bool = False,
    ) -> ArtifactCard:
        raise ValueError("ProjectCardRegistry does not support load_card")

    def delete_card(self, card: ArtifactCard) -> None:
        raise ValueError("ProjectCardRegistry does not support delete_card")


# CardRegistry also needs to set a storage file system
class CardRegistry:
    def __init__(self, registry_name: str):
        """
        Interface for connecting to any of the ArtifactCard registries

        Args:
            registry_name:
                Name of the registry to connect to. Options are "model", "data" and "run".

        Returns:
            Instantiated connection to specific Card registry

        Example:
            data_registry = CardRegistry(registry_name="data")
        """

        self._registry = self._set_registry(registry_name=registry_name)
        self.table_name = self._registry._table.__tablename__

    def _set_registry(self, registry_name: str) -> Registry:
        """Returns a SQL registry to be used to register Cards

        Args:
            registry_name: Name of the registry (pipeline, model, data, experiment)

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
        as_dataframe: bool = False,
        ignore_release_candidates: bool = False,
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
            as_dataframe:
                If True, returns a pandas dataframe. If False, returns a list of records
            info:
                CardInfo object. If present, the info object takes precedence
            ignore_release_candidates:
                If True, ignores release candidates

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
            ignore_release_candidates=ignore_release_candidates,
        )

        if as_dataframe:
            return pd.DataFrame(card_list)

        return card_list

    def load_card(
        self,
        name: Optional[str] = None,
        uid: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        version: Optional[str] = None,
        info: Optional[CardInfo] = None,
        ignore_release_candidates: bool = False,
    ) -> ArtifactCard:
        """Loads a specific card

        Args:
            name:
                Optional Card name
            uid:
                Unique identifier for card. If present, the uid takes
                precedence.
            tags:
                Optional tags associated with model.
            version:
                Optional version number of existing data. If not specified, the
                most recent version will be used
            info:
                Optional CardInfo object. If present, the info takes precedence
            ignore_release_candidates:
                If True, ignores release candidates

        Returns
            ArtifactCard
        """

        # find better way to do this later
        if info is not None:
            name = name or info.name
            uid = uid or info.uid
            version = version or info.version
            tags = tags or info.tags

        return self._registry.load_card(
            uid=uid,
            name=name,
            version=version,
            tags=tags,
            ignore_release_candidates=ignore_release_candidates,
        )

    def register_card(
        self,
        card: ArtifactCard,
        version_type: VersionType = VersionType.MINOR,
        pre_tag: str = "rc",
        build_tag: str = "build",
    ) -> None:
        """
        Adds a new `Card` record to registry. Registration will be skipped if the card already exists.

        Args:
            card:
                card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor".
            pre_tag:
                pre-release tag to add to card version
            build_tag:
                build tag to add to card version
        """

        if card.uid is not None:
            logger.info(
                textwrap.dedent(
                    f"""
                Card {card.uid} already exists. Skipping registration. If you'd like to register 
                a new card, please instantiate a new Card object. If you'd like to update the 
                existing card, please use the update_card method.
                """
                )
            )

        else:
            self._registry.register_card(
                card=card,
                version_type=version_type,
                pre_tag=pre_tag,
                build_tag=build_tag,
            )

    def update_card(self, card: ArtifactCard) -> None:
        """
        Update an artifact card based on current registry

        Args:
            card:
                Card to register
        """
        return self._registry.update_card(card=card)

    def query_value_from_card(self, uid: str, columns: List[str]) -> Dict[str, Any]:
        """
        Query column values from a specific Card

        Args:
            uid:
                Uid of Card
            columns:
                List of columns to query

        Returns:
            Dictionary of column, values pairs
        """
        results = self._registry.list_cards(uid=uid)[0]
        return {col: results[col] for col in columns}

    def delete_card(self, card: ArtifactCard) -> None:
        """
        Delete a specific Card

        Args:
            card:
                Card to delete
        """
        return self._registry.delete_card(card)


class CardRegistries:
    def __init__(self):
        """Instantiates class that contains all registries"""
        self.data = CardRegistry(registry_name=CardType.DATACARD.value)
        self.model = CardRegistry(registry_name=CardType.MODELCARD.value)
        self.run = CardRegistry(registry_name=CardType.RUNCARD.value)
        self.pipeline = CardRegistry(registry_name=CardType.PIPELINECARD.value)
        self.project = CardRegistry(registry_name=CardType.PROJECTCARD.value)

    def set_storage_client(self, storage_client: StorageClientType):
        for attr in ["data", "model", "run", "project", "pipeline"]:
            registry: CardRegistry = getattr(self, attr)
            registry._registry.storage_client = storage_client
