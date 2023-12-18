# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import textwrap
from typing import Any, Dict, List, Optional, Type, Union, cast

import pandas as pd

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards import (
    ArtifactCard,
    AuditCard,
    CardInfo,
    DataCard,
    ModelCard,
    PipelineCard,
    RunCard,
)
from opsml.registry.sql.base.registry_base import SQLRegistryBase
from opsml.registry.sql.semver import VersionType
from opsml.registry.storage import client
from opsml.registry.types import RegistryType
from opsml.settings.config import config

logger = ArtifactLogger.get_logger()

table_name_card_map = {
    RegistryType.DATA.value: DataCard,
    RegistryType.MODEL.value: ModelCard,
    RegistryType.RUN.value: RunCard,
    RegistryType.PIPELINE.value: PipelineCard,
    RegistryType.AUDIT.value: AuditCard,
}


class CardRegistry:
    def __init__(self, registry_type: RegistryType, storage_client: client.StorageClientType):
        """
        Interface for connecting to any of the ArtifactCard registries

        Args:
            registry_type:
                Type of card registry to create
            settings:
                Storage settings

        Returns:
            Instantiated connection to specific Card registry

        Example:
            data_registry = CardRegistry(RegistryType.DATA, settings)s
        """

        self._registry = self._set_registry(registry_type, storage_client)
        self.table_name = self._registry.table_name

    @property
    def registry_type(self) -> RegistryType:
        "Registry type for card registry"
        return self._registry.registry_type

    def _set_registry(self, registry_type: RegistryType, storage_client: client.StorageClientType) -> SQLRegistryBase:
        """Sets the underlying registry.

        IMPORTANT: We need to delay importing ServerRegistry until we know we
        need it. Since opsml can run in both "server" mode (where tracking is
        local) which requires sqlalchemy and "client" mode which does not, we
        only want to import ServerRegistry when we know we need it.
        """
        sql_registry_type: Type[SQLRegistryBase]
        if config.is_tracking_local:
            from opsml.registry.sql.base.server import ServerRegistry

            sql_registry_type = ServerRegistry
        else:
            from opsml.registry.sql.base.client import ClientRegistry

            sql_registry_type = ClientRegistry

        registry = next(
            registry
            for registry in sql_registry_type.__subclasses__()
            if registry.validate(
                registry_name=registry_type.value,
            )
        )
        return registry(registry_type=registry_type, storage_client=storage_client)

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

        if all(not bool(var) for var in [name, team, version, uid, tags]):
            limit = limit or 25

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

        record = self._registry.load_card_record(
            uid=uid,
            name=name,
            version=version,
            tags=tags,
            ignore_release_candidates=ignore_release_candidates,
        )
        card = table_name_card_map[self.registry_type.value]
        return cast(ArtifactCard, card(**record.model_dump()))

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

        if card.uid is not None and card.version is not None:
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
    def __init__(self, storage_client: Optional[client.StorageClientType] = None) -> None:
        """Instantiates class that contains all registries"""
        if storage_client is None:
            storage_client = client.storage_client

        self.data = CardRegistry(registry_type=RegistryType.DATA, storage_client=storage_client)
        self.model = CardRegistry(registry_type=RegistryType.MODEL, storage_client=storage_client)
        self.run = CardRegistry(registry_type=RegistryType.RUN, storage_client=storage_client)
        self.pipeline = CardRegistry(registry_type=RegistryType.PIPELINE, storage_client=storage_client)
        self.project = CardRegistry(registry_type=RegistryType.PROJECT, storage_client=storage_client)
        self.audit = CardRegistry(registry_type=RegistryType.AUDIT, storage_client=storage_client)
