# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import textwrap
from typing import Any, Dict, List, Optional, Type, Union

from opsml.cards import ArtifactCard, CardInfo
from opsml.data import DataInterface
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import clean_string
from opsml.model import ModelInterface
from opsml.registry.backend import _set_registry
from opsml.registry.semver import VersionType
from opsml.storage.card_loader import CardLoader
from opsml.types import CommonKwargs, RegistryType

logger = ArtifactLogger.get_logger()


class CardRegistry:
    def __init__(self, registry_type: Union[RegistryType, str]):
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
            data_registry = CardRegistry(RegistryType.DATA)
            data_registry.list_cards()

            or
            data_registry = CardRegistry("data")
            data_registry.list_cards()
        """

        _registry_type = (
            registry_type if isinstance(registry_type, RegistryType) else RegistryType.from_str(registry_type)
        )

        self._registry = _set_registry(_registry_type)
        self.table_name = self._registry.table_name

    @property
    def registry_type(self) -> RegistryType:
        "Registry type for card registry"
        return self._registry.registry_type

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        info: Optional[CardInfo] = None,
        max_date: Optional[str] = None,
        limit: Optional[int] = None,
        ignore_release_candidates: bool = False,
    ) -> List[Dict[str, Any]]:
        """Retrieves records from registry

        Args:
            name:
                Card name
            repository:
                Repository associated with card
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
            info:
                CardInfo object. If present, the info object takes precedence
            ignore_release_candidates:
                If True, ignores release candidates

        Returns:
            pandas dataframe of records or list of dictionaries
        """

        if info is not None:
            name = name or info.name
            repository = repository or info.repository
            uid = uid or info.uid
            version = version or info.version
            tags = tags or info.tags

        if name is not None:
            name = name.lower()

        if repository is not None:
            repository = repository.lower()

        if all(not bool(var) for var in [name, repository, version, uid, tags]):
            limit = limit or 25

        card_list = self._registry.list_cards(
            uid=uid,
            name=name,
            repository=repository,
            version=version,
            max_date=max_date,
            limit=limit,
            tags=tags,
            ignore_release_candidates=ignore_release_candidates,
        )

        return card_list

    def load_card(
        self,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        uid: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        version: Optional[str] = None,
        info: Optional[CardInfo] = None,
        ignore_release_candidates: bool = False,
        interface: Optional[Union[Type[ModelInterface], Type[DataInterface]]] = None,
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
            repository:
                Optional repository associated with card
            version:
                Optional version number of existing data. If not specified, the
                most recent version will be used
            info:
                Optional CardInfo object. If present, the info takes precedence
            ignore_release_candidates:
                If True, ignores release candidates
            interface:
                Optional interface to use for loading card. This is required for when using
                subclassed interfaces.

        Returns
            ArtifactCard
        """

        # find better way to do this later
        if info is not None:
            name = name or info.name
            uid = uid or info.uid
            version = version or info.version
            tags = tags or info.tags

        name = clean_string(name)

        records = self.list_cards(
            uid=uid,
            name=name,
            repository=repository,
            version=version,
            tags=tags,
            ignore_release_candidates=ignore_release_candidates,
            limit=1,
        )

        return CardLoader(
            card_args=records[0],
            registry_type=self.registry_type,
        ).load_card(interface=interface)

    def register_card(
        self,
        card: ArtifactCard,
        version_type: Union[VersionType, str] = VersionType.MINOR,
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

        _version_type = version_type if isinstance(version_type, VersionType) else VersionType.from_str(version_type)

        if card.uid is not None and card.version != CommonKwargs.BASE_VERSION.value:
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
                version_type=_version_type,
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
    def __init__(self) -> None:
        """Instantiates class that contains all registries"""

        self.data = CardRegistry(registry_type=RegistryType.DATA)
        self.model = CardRegistry(registry_type=RegistryType.MODEL)
        self.run = CardRegistry(registry_type=RegistryType.RUN)
        self.pipeline = CardRegistry(registry_type=RegistryType.PIPELINE)
        self.project = CardRegistry(registry_type=RegistryType.PROJECT)
        self.audit = CardRegistry(registry_type=RegistryType.AUDIT)
