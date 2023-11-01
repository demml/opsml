# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict, List, Optional, Tuple

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import clean_string
from opsml.registry.sql.base.registry_base import SQLRegistryBase
from opsml.registry.sql.base.query_engine import QueryEngine, log_card_change  # type: ignore
from opsml.registry.sql.semver import SemVerSymbols, CardVersion, VersionType, SemVerUtils, SemVerRegistryValidator

logger = ArtifactLogger.get_logger()


class ServerRegistry(SQLRegistryBase):
    def __init__(self, table_name: str):
        super().__init__(table_name)
        self.engine = QueryEngine()

    def _create_table_if_not_exists(self):
        self._table.__table__.create(
            bind=self.engine.engine,
            checkfirst=True,
        )

    def _get_versions_from_db(self, name: str, team: str, version_to_search: Optional[str] = None) -> List[str]:
        """Query versions from Card Database

        Args:
            name:
                Card name
            team:
                Card team
            version_to_search:
                Version to search for
        Returns:
            List of versions
        """
        results = self.engine.get_versions(table=self._table, name=name, version=version_to_search)

        if bool(results):
            if results[0].team != team:
                raise ValueError("""Model name already exists for a different team. Try a different name.""")

            versions = [result.version for result in results]
            return SemVerUtils.sort_semvers(versions=versions)
        return []

    def set_version(
        self,
        name: str,
        team: str,
        pre_tag: str,
        build_tag: str,
        version_type: VersionType,
        supplied_version: Optional[CardVersion] = None,
    ) -> str:
        """
        Sets a version following semantic version standards

        Args:
            name:
                Card name
            team:
                Card team
            pre_tag:
                Pre-release tag
            build_tag:
                Build tag
            version_type:
                Version type
            supplied_version:
                Optional version to set. If not specified, will use the most recent version

        Returns:
            Version string
        """

        ver_validator = SemVerRegistryValidator(
            version_type=version_type,
            version=supplied_version,
            name=name,
            pre_tag=pre_tag,
            build_tag=build_tag,
        )

        versions = self._get_versions_from_db(
            name=name,
            team=team,
            version_to_search=ver_validator.version_to_search,
        )

        return ver_validator.set_version(versions=versions)

    @log_card_change
    def add_and_commit(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        self.engine.add_and_commit_card(table=self._table, card=card)
        return card, "registered"

    @log_card_change
    def update_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        self.engine.update_card_record(table=self._table, card=card)
        return card, "updated"

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        max_date: Optional[str] = None,
        limit: Optional[int] = None,
        ignore_release_candidates: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves records from registry

        Args:
            name:
                Artifact record name
            team:
                Team data is assigned to
            version:
                Optional version number of existing data. If not specified,
                the most recent version will be used. Version can also include tilde (~), caret (^) and * characters.
            tags:
                Dictionary of key, value tags to search for
            uid:
                Unique identifier for DataCard. If present, the uid takes precedence.
            max_date:
                Max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01")
            limit:
                Places a limit on result list. Results are sorted by SemVer
            ignore_release_candidates:
                If True, will ignore release candidates when searching for versions


        Returns:
            Dictionary of records
        """

        cleaned_name = clean_string(name)
        cleaned_team = clean_string(team)

        records = self.engine.get_records_from_table(
            table=self._table,
            name=cleaned_name,
            team=cleaned_team,
            version=version,
            uid=uid,
            max_date=max_date,
            tags=tags,
        )

        records = self._sort_by_version(records=records)

        if version is not None:
            if ignore_release_candidates:
                records = [record for record in records if not SemVerUtils.is_release_candidate(record["version"])]
            if any(symbol in version for symbol in [SemVerSymbols.CARET, SemVerSymbols.TILDE]):
                # return top version
                return records[:1]

        if version is None and ignore_release_candidates:
            records = [record for record in records if not SemVerUtils.is_release_candidate(record["version"])]

        return records[:limit]

    def check_uid(self, uid: str, table_to_check: str) -> bool:
        result = self.engine.get_uid(
            uid=uid,
            table_to_check=table_to_check,
        )
        return bool(result)

    @log_card_change
    def delete_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Deletes a card record from the backend database"""
        self.engine.delete_card_record(table=self._table, card=card)
        return card, "deleted"

    @staticmethod
    def validate(registry_name: str) -> bool:
        raise NotImplementedError
