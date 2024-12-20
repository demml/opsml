# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from semver import VersionInfo

from opsml.cards import Card
from opsml.helpers.exceptions import CardDeleteError, VersionError
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.records import SaveRecord, registry_name_record_map
from opsml.registry.semver import CardVersion, SemVerUtils, VersionType
from opsml.settings.config import config
from opsml.storage.card_saver import save_card_artifacts
from opsml.storage.client import StorageClient
from opsml.types import RegistryTableNames, RegistryType
from opsml.types.extra import CommonKwargs

logger = ArtifactLogger.get_logger()


class SQLRegistryBase:
    def __init__(self, registry_type: RegistryType, storage_client: StorageClient):
        """
        Base class for SQL Registries to inherit from

        Args:
            registry_type:
                Registry type
        """
        self.storage_client = storage_client
        self._table_name = RegistryTableNames[registry_type.value.upper()].value
        self._registry_type = registry_type

    @property
    def unique_repositories(self) -> Sequence[str]:
        raise NotImplementedError

    def query_stats(self, search_term: Optional[str]) -> Dict[str, int]:
        raise NotImplementedError

    def query_page(
        self,
        sort_by: str,
        page: int,
        repository: Optional[str] = None,
        search_term: Optional[str] = None,
    ) -> List[List[Union[str, int]]]:
        raise NotImplementedError

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def supported_card(self) -> str:
        return f"{self.table_name.split('_')[1]}Card"

    def set_version(
        self,
        name: str,
        repository: str,
        pre_tag: str,
        build_tag: str,
        version_type: VersionType,
        supplied_version: Optional[CardVersion] = None,
    ) -> str:
        raise NotImplementedError

    def _is_correct_card_type(self, card: Card) -> bool:
        """Checks wether the current card is associated with the correct registry type"""
        return self.supported_card.lower() == card.__class__.__name__.lower()

    @property
    def registry_type(self) -> RegistryType:
        """Registry type"""
        raise NotImplementedError

    def _get_uid(self) -> str:
        """Sets a unique id to be applied to a card"""
        return uuid.uuid4().hex

    def add_and_commit(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        raise NotImplementedError

    def update_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        raise NotImplementedError

    def delete_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        raise NotImplementedError

    @staticmethod
    def validate(registry_name: str) -> bool:
        raise NotImplementedError

    def _validate_card_type(self, card: Card) -> None:
        # check compatibility
        if not self._is_correct_card_type(card=card):
            raise ValueError(
                f"""Card of type {card.__class__.__name__} is not supported by registry
                {self.table_name}"""
            )

        if self.check_uid(uid=str(card.uid), registry_type=self.registry_type):
            raise ValueError(
                """This Card has already been registered.
            If the card has been modified try updating the Card in the registry.
            If registering a new Card, create a new Card of the correct type.
            """
            )

    def _validate_semver(self, name: str, repository: str, version: CardVersion) -> None:
        """
        Validates version if version is manually passed to Card

        Args:
            name:
                Name of card
            repository:
                Repository of card
            version:
                Version of card
        Returns:
            `CardVersion`
        """
        if version.is_full_semver:
            records = self.list_cards(name=name, version=version.valid_version)
            if len(records) > 0:
                for record in records:
                    ver = VersionInfo.parse(record["version"])

                    if ver.prerelease is None and SemVerUtils.is_release_candidate(version.version):
                        raise VersionError(
                            f"Cannot create a release candidate for an existing official version. {version.version}"
                        )

                    if record["version"] == version.version:
                        raise VersionError(f"Version combination already exists. {version.version}")

    def _validate_pre_build_version(self, version: Optional[str] = None) -> CardVersion:
        if version == CommonKwargs.BASE_VERSION.value:
            raise ValueError("Cannot set pre-release or build tag without a version")
        card_version = CardVersion(version=version)

        if not card_version.is_full_semver:
            raise ValueError("Cannot set pre-release or build tag without a full major.minor.patch specified")

        return card_version

    def _set_card_version(
        self,
        card: Card,
        version_type: VersionType,
        pre_tag: str,
        build_tag: str,
    ) -> None:
        """Sets a given card's version and uid

        Args:
            card:
                Card to set
            version_type:
                Type of version increment
        """

        card_version = None
        assert card.name is not None
        assert card.repository is not None

        # validate pre-release and/or build tag
        if version_type in [VersionType.PRE, VersionType.BUILD, VersionType.PRE_BUILD]:
            card_version = self._validate_pre_build_version(version=card.version)

        # if DS specifies version and not release candidate
        if card.version != CommonKwargs.BASE_VERSION.value and version_type not in [
            VersionType.PRE,
            VersionType.PRE_BUILD,
        ]:
            # build tags are allowed with "official" versions
            if version_type == VersionType.BUILD:
                # check whether DS-supplied version has a build tag already
                if VersionInfo.parse(card.version).build is None:
                    card.version = self.set_version(
                        name=card.name,
                        supplied_version=card_version,
                        repository=card.repository,
                        version_type=version_type,
                        pre_tag=pre_tag,
                        build_tag=build_tag,
                    )

            card_version = CardVersion(version=card.version)
            if card_version.is_full_semver:
                self._validate_semver(name=card.name, repository=card.repository, version=card_version)
                return None

        version = self.set_version(
            name=card.name,
            supplied_version=card_version,
            repository=card.repository,
            version_type=version_type,
            pre_tag=pre_tag,
            build_tag=build_tag,
        )

        # for instances where tag is explicitly provided for major, minor, patch
        if version_type in [VersionType.MAJOR, VersionType.MINOR, VersionType.PATCH]:
            if len(pre_tag.split(".")) == 2:
                version = f"{version}-{pre_tag}"

            if len(build_tag.split(".")) == 2:
                version = f"{version}+{build_tag}"

        card.version = version

        return None

    def _set_card_uid(self, card: Card) -> None:
        """Sets a given card's uid

        Args:
            card:
                Card to set
        """
        if card.uid is None:
            card.uid = self._get_uid()

    def register_card(
        self,
        card: Card,
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
                Version type for increment. Options are "major", "minor" and "patch". Defaults to "minor"
            pre_tag:
                Pre-release tag. Defaults to "rc"
            build_tag:
                Build tag. Defaults to "build"
        """

        self._validate_card_type(card=card)
        self._set_card_version(card=card, version_type=version_type, pre_tag=pre_tag, build_tag=build_tag)
        self._set_card_uid(card=card)

        save_card_artifacts(card=card)
        registry_record: SaveRecord = registry_name_record_map[card.card_type]
        record = registry_record.model_validate(card.create_registry_record())

        self.add_and_commit(card=record.model_dump())

    def _card_with_diff_uid_already_exists(self, card: Card) -> bool:
        """Check if a card with a different uid already exists for a given name, repository and version

        Args:
            card:
                Card to check

        Returns:
            boolean

        """
        # check new card does not overwrite existing name, repository and version with a different uid
        _current_record = self.list_cards(name=card.name, repository=card.repository, version=card.version)
        if _current_record:
            if _current_record[0]["uid"] != card.uid:
                return True

        return False

    def _cleanup_card_artifacts(self, record: Dict[str, Any], card: Card) -> None:
        """Removes card artifacts from storage

        Args:
            card:
                Card to remove
        """
        # when moving objects to a new uri, remove the previous uri and its contents
        repository, name, version = record["repository"], record["name"], record["version"]

        previous_uri = Path(
            f"{config.storage_root}/{RegistryTableNames.from_str(card.card_type).value}/{repository}/{name}/v{version}"
        )

        if previous_uri != card.uri:
            logger.info("Uri has changed. Removing previous uri {}", previous_uri)
            self.storage_client.rm(previous_uri)

    def update_card(self, card: Card) -> None:
        """
        Updates a registry record.

        Args:
            card:
                Card to update
        """
        # checking card exists
        record = self.list_cards(uid=card.uid, limit=1)
        assert bool(record), "Card does not exist in registry. Please use register card first"

        if self._card_with_diff_uid_already_exists(card):
            logger.error(
                "Card for {}/{}/{} already exists with a different uid", card.repository, card.name, card.version
            )
            raise ValueError(
                f"Card for {card.repository}/{card.name}/{card.version} already exists with a different uid"
            )

        logger.info("Updating card {}/{}/{}", card.repository, card.name, card.version)

        save_card_artifacts(card=card)

        save_record: SaveRecord = registry_name_record_map[card.card_type](**card.create_registry_record())
        self.update_card_record(card=save_record.model_dump())
        self._cleanup_card_artifacts(record[0], card)

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        max_date: Optional[str] = None,
        limit: Optional[int] = None,
        ignore_release_candidates: bool = False,
        query_terms: Optional[Dict[str, Any]] = None,
        sort_by_timestamp: bool = False,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def check_uid(self, uid: str, registry_type: RegistryType) -> bool:
        raise NotImplementedError

    def _sort_by_version(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        versions = [record["version"] for record in records]
        sorted_versions = SemVerUtils.sort_semvers(versions)

        sorted_records = []
        for version in sorted_versions:
            for record in records:
                if record["version"] == version:
                    sorted_records.append(record)

        return sorted_records

    def _sort_by_timestamp(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(records, key=lambda k: k["timestamp"], reverse=True)

    def delete_card(self, card: Card) -> None:
        """Delete a specific card"""

        try:
            # delete card record before storage artifacts (there will be loading issues if objects are deleted but not the record)
            self.delete_card_record(card=card.model_dump(include={"uid", "name", "version"}))
            self.storage_client.rm(card.uri)
        except CardDeleteError as err:
            raise CardDeleteError(f"Failed to delete card {card.name} from registry {self.table_name}") from err
