# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, cast, Iterator

import pandas as pd
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import ColumnElement, FromClause, Select
from semver import VersionInfo
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import api_routes
from opsml.helpers.utils import clean_string
from opsml.registry.cards.card_saver import save_card_artifacts
from opsml.registry.cards import (
    ArtifactCard,
    DataCard,
    ModelCard,
    PipelineCard,
    RunCard,
)
from opsml.registry.sql.query_helpers import QueryCreator, log_card_change  # type: ignore
from opsml.registry.sql.records import LoadedRecordType, load_record
from opsml.registry.sql.semver import SemVerSymbols, CardVersion, VersionType, SemVerUtils, SemVerRegistryValidator
from opsml.registry.sql.settings import settings
from opsml.registry.sql.sql_schema import RegistryTableNames, TableSchema
from opsml.helpers.exceptions import VersionError
from opsml.registry.storage.types import ArtifactStorageSpecs

logger = ArtifactLogger.get_logger(__name__)


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]

# initialize tables
if settings.request_client is None:
    from opsml.registry.sql.db_initializer import DBInitializer

    initializer = DBInitializer(
        engine=settings.connection_client.get_engine(),
        registry_tables=list(RegistryTableNames),
    )
    initializer.initialize()

query_creator = QueryCreator()

table_name_card_map = {
    RegistryTableNames.DATA.value: DataCard,
    RegistryTableNames.MODEL.value: ModelCard,
    RegistryTableNames.RUN.value: RunCard,
    RegistryTableNames.PIPELINE.value: PipelineCard,
}


def load_card_from_record(
    table_name: str,
    record: LoadedRecordType,
) -> ArtifactCard:
    """
    Loads an artifact card given a tablename and the loaded record
    from backend database

    Args:
        table_name:
            Name of table
        record:
            Loaded record from backend database

    Returns:
        `ArtifactCard`
    """

    card = table_name_card_map[table_name]
    return card(**record.model_dump())


class SQLRegistryBase:
    def __init__(self, table_name: str):
        """
        Base class for SQL Registries to inherit from

        Args:
            table_name:
                CardRegistry table name
        """
        self.table_name = table_name
        self.supported_card = f"{table_name.split('_')[1]}Card"
        self.storage_client = settings.storage_client

        self._table = TableSchema.get_table(table_name=table_name)

    def set_version(
        self,
        name: str,
        team: str,
        pre_tag: str,
        build_tag: str,
        version_type: VersionType,
        supplied_version: Optional[CardVersion] = None,
    ) -> str:
        raise NotImplementedError

    def _is_correct_card_type(self, card: ArtifactCard):
        """Checks wether the current card is associated with the correct registry type"""
        return self.supported_card.lower() == card.__class__.__name__.lower()

    def _get_uid(self) -> str:
        """Sets a unique id to be applied to a card"""
        return uuid.uuid4().hex

    def add_and_commit(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        raise NotImplementedError

    def update_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        raise NotImplementedError

    def _validate_card_type(self, card: ArtifactCard):
        # check compatibility
        if not self._is_correct_card_type(card=card):
            raise ValueError(
                f"""Card of type {card.__class__.__name__} is not supported by registry
                {self._table.__tablename__}"""
            )

        if self.check_uid(uid=str(card.uid), table_to_check=self.table_name):
            raise ValueError(
                """This Card has already been registered.
            If the card has been modified try updating the Card in the registry.
            If registering a new Card, create a new Card of the correct type.
            """
            )

    def _set_artifact_storage_spec(self, card: ArtifactCard) -> None:
        """Creates artifact storage info to associate with artifacts"""

        save_path = f"{self.table_name}/{card.team}/{card.name}/v{card.version}"

        artifact_storage_spec = ArtifactStorageSpecs(save_path=save_path)
        self._update_storage_client_metadata(storage_specdata=artifact_storage_spec)

    def _update_storage_client_metadata(self, storage_specdata: ArtifactStorageSpecs):
        """Updates storage metadata"""
        self.storage_client.storage_spec = storage_specdata

    def _validate_semver(self, name: str, team: str, version: CardVersion) -> None:
        """
        Validates version if version is manually passed to Card

        Args:
            name:
                Name of card
            team:
                Team of card
            version:
                Version of card
        Returns:
            `CardVersion`
        """
        if version.is_full_semver:
            records = self.list_cards(name=name, version=version.valid_version)
            if len(records) > 0:
                if records[0]["team"] != team:
                    raise ValueError("""Model name already exists for a different team. Try a different name.""")

                for record in records:
                    ver = VersionInfo.parse(record["version"])

                    if ver.prerelease is None and SemVerUtils.is_release_candidate(version.version):
                        raise VersionError(
                            "Cannot create a release candidate for an existing official version. %s" % version.version
                        )

                    if record["version"] == version.version:
                        raise VersionError("Version combination already exists. %s" % version.version)

    def _validate_pre_build_version(self, version: Optional[str] = None) -> CardVersion:
        if version is None:
            raise ValueError("Cannot set pre-release or build tag without a version")
        card_version = CardVersion(version=version)

        if not card_version.is_full_semver:
            raise ValueError("Cannot set pre-release or build tag without a full major.minor.patch specified")

        return card_version

    def _set_card_version(
        self,
        card: ArtifactCard,
        version_type: VersionType,
        pre_tag: str,
        build_tag: str,
    ):
        """Sets a given card's version and uid

        Args:
            card:
                Card to set
            version_type:
                Type of version increment
        """

        card_version = None

        # validate pre-release and/or build tag
        if version_type in [VersionType.PRE, VersionType.BUILD, VersionType.PRE_BUILD]:
            card_version = self._validate_pre_build_version(version=card.version)

        # if DS specifies version and not release candidate
        if card.version is not None and version_type not in [VersionType.PRE, VersionType.PRE_BUILD]:
            # build tags are allowed with "official" versions
            if version_type == VersionType.BUILD:
                # check whether DS-supplied version has a build tag already
                if VersionInfo.parse(card.version).build is None:
                    card.version = self.set_version(
                        name=card.name,
                        supplied_version=card_version,
                        team=card.team,
                        version_type=version_type,
                        pre_tag=pre_tag,
                        build_tag=build_tag,
                    )

            card_version = CardVersion(version=card.version)
            if card_version.is_full_semver:
                self._validate_semver(name=card.name, team=card.team, version=card_version)
                return None

        version = self.set_version(
            name=card.name,
            supplied_version=card_version,
            team=card.team,
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

    def _set_card_uid(self, card: ArtifactCard) -> None:
        """Sets a given card's uid

        Args:
            card:
                Card to set
        """
        if card.uid is None:
            card.uid = self._get_uid()

    def _create_registry_record(self, card: ArtifactCard) -> None:
        """
        Creates a registry record from a given ArtifactCard.
        Saves artifacts prior to creating record

        Args:
            card:
                Card to create a registry record from
        """

        card = save_card_artifacts(card=card, storage_client=self.storage_client)
        record = card.create_registry_record()

        self.add_and_commit(card=record.model_dump())

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
                Version type for increment. Options are "major", "minor" and "patch". Defaults to "minor"
        """

        self._validate_card_type(card=card)
        self._set_card_version(
            card=card,
            version_type=version_type,
            pre_tag=pre_tag,
            build_tag=build_tag,
        )
        self._set_card_uid(card=card)
        self._set_artifact_storage_spec(card=card)
        self._create_registry_record(card=card)

    def update_card(self, card: ArtifactCard) -> None:
        """
        Updates a registry record.

        Args:
            card:
                Card to update
        """
        card = save_card_artifacts(card=card, storage_client=self.storage_client)
        record = card.create_registry_record()
        self.update_card_record(card=record.model_dump())

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
        raise NotImplementedError

    def check_uid(self, uid: str, table_to_check: str) -> bool:
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

    def load_card(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        uid: Optional[str] = None,
        ignore_release_candidates: bool = False,
    ) -> ArtifactCard:
        cleaned_name = clean_string(name)

        record = self.list_cards(
            name=cleaned_name,
            version=version,
            uid=uid,
            limit=1,
            tags=tags,
            ignore_release_candidates=ignore_release_candidates,
        )

        loaded_record = load_record(
            table_name=self.table_name,
            record_data=record[0],
            storage_client=self.storage_client,
        )

        return load_card_from_record(
            table_name=self.table_name,
            record=loaded_record,
        )


class ServerRegistry(SQLRegistryBase):
    def __init__(self, table_name: str):
        super().__init__(table_name)
        self.table_name = self._table.__tablename__

    def _get_engine(self):
        return settings.connection_client.get_engine()

    @contextmanager  # type: ignore
    def session(self) -> Iterator[Session]:
        engine = self._get_engine()

        with Session(engine) as sess:  # type: ignore
            yield sess

    def _create_table_if_not_exists(self):
        engine = self._get_engine()
        self._table.__table__.create(bind=engine, checkfirst=True)

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
        query = query_creator.create_version_query(table=self._table, name=name, version=version_to_search)

        with self.session() as sess:
            results = sess.scalars(query).all()  # type: ignore[attr-defined]

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
            partial_version:
                Validated partial version to set. If None, will increment the latest version
            version_type:
                Type of version increment. Values are "major", "minor" and "patch

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
        sql_record = self._table(**card)

        with self.session() as sess:
            sess.add(sql_record)
            sess.commit()

        return card, "registered"

    @log_card_change
    def update_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        record_uid = cast(str, card.get("uid"))

        with self.session() as sess:
            query = sess.query(self._table).filter(self._table.uid == record_uid)
            query.update(card)
            sess.commit()

        return card, "updated"

    def _parse_sql_results(self, results: Any) -> List[Dict[str, Any]]:
        """
        Helper for parsing sql results

        Args:
            results:
                Returned object sql query

        Returns:
            List of dictionaries
        """
        records: List[Dict[str, Any]] = []

        for row in results:
            result_dict = row[0].__dict__
            result_dict.pop("_sa_instance_state")
            records.append(result_dict)

        return records

    def _get_sql_records(self, query: Select) -> List[Dict[str, Any]]:
        """
        Gets sql records from database given a query

        Args:
            query:
                sql query
        Returns:
            List of records
        """

        with self.session() as sess:
            results = sess.execute(query).all()

        records = self._parse_sql_results(results=results)

        sorted_records = self._sort_by_version(records=records)

        return sorted_records

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


        Returns:
            Dictionary of records
        """

        cleaned_name = clean_string(name)
        cleaned_team = clean_string(team)

        query = query_creator.record_from_table_query(
            table=self._table,
            name=cleaned_name,
            team=cleaned_team,
            version=version,
            uid=uid,
            max_date=max_date,
            tags=tags,
        )

        sorted_records = self._get_sql_records(query=query)

        if version is not None:
            if ignore_release_candidates:
                sorted_records = [
                    record for record in sorted_records if not SemVerUtils.is_release_candidate(record["version"])
                ]
            if any(symbol in version for symbol in [SemVerSymbols.CARET, SemVerSymbols.TILDE]):
                # return top version
                return sorted_records[:1]

        if version is None and ignore_release_candidates:
            sorted_records = [
                record for record in sorted_records if not SemVerUtils.is_release_candidate(record["version"])
            ]

        return sorted_records[:limit]

    def check_uid(self, uid: str, table_to_check: str) -> bool:
        query = query_creator.uid_exists_query(
            uid=uid,
            table_to_check=table_to_check,
        )
        with self.session() as sess:
            result = sess.scalars(query).first()  # type: ignore[attr-defined]
        return bool(result)

    @staticmethod
    def validate(registry_name: str) -> bool:
        raise NotImplementedError


class ClientRegistry(SQLRegistryBase):
    def __init__(self, table_name: str):
        super().__init__(table_name)

        self._session = self._get_session()

    def _get_session(self):
        """Gets the requests session for connecting to the opsml api"""
        return settings.request_client

    def check_uid(self, uid: str, table_to_check: str) -> bool:
        data = self._session.post_request(
            route=api_routes.CHECK_UID,
            json={"uid": uid, "table_name": table_to_check},
        )

        return bool(data.get("uid_exists"))

    def set_version(
        self,
        name: str,
        team: str,
        pre_tag: str,
        build_tag: str,
        version_type: VersionType = VersionType.MINOR,
        supplied_version: Optional[CardVersion] = None,
    ) -> str:
        if supplied_version is not None:
            version_to_send = supplied_version.model_dump()
        else:
            version_to_send = None

        data = self._session.post_request(
            route=api_routes.VERSION,
            json={
                "name": name,
                "team": team,
                "version": version_to_send,
                "version_type": version_type,
                "table_name": self.table_name,
                "pre_tag": pre_tag,
                "build_tag": build_tag,
            },
        )

        return data.get("version")

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
    ) -> pd.DataFrame:
        """
        Retrieves records from registry

        Args:
            name:
                Card Name
            team:
                Team Card
            version:
                Version. If not specified, the most recent version will be used.
            uid:
                Unique identifier for an ArtifactCard. If present, the uid takes precedence.
            tags:
                Tags associated with a given ArtifactCard
            max_date:
                Max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01")
            limit:
                Places a limit on result list. Results are sorted by SemVer

        Returns:
            Dictionary of card records
        """
        data = self._session.post_request(
            route=api_routes.LIST_CARDS,
            json={
                "name": name,
                "team": team,
                "version": version,
                "uid": uid,
                "max_date": max_date,
                "limit": limit,
                "tags": tags,
                "table_name": self.table_name,
                "ignore_release_candidates": ignore_release_candidates,
            },
        )

        return data["cards"]

    @log_card_change
    def add_and_commit(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.post_request(
            route=api_routes.CREATE_CARD,
            json={
                "card": card,
                "table_name": self.table_name,
            },
        )

        if bool(data.get("registered")):
            return card, "registered"
        raise ValueError("Failed to register card")

    @log_card_change
    def update_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.post_request(
            route=api_routes.UPDATE_CARD,
            json={
                "card": card,
                "table_name": self.table_name,
            },
        )

        if bool(data.get("updated")):
            return card, "updated"
        raise ValueError("Failed to update card")

    @staticmethod
    def validate(registry_name: str) -> bool:
        raise NotImplementedError


# mypy not happy with dynamic classes
def get_sql_registry_base():
    if settings.request_client is not None:
        return ClientRegistry
    return ServerRegistry


OpsmlRegistry = get_sql_registry_base()
