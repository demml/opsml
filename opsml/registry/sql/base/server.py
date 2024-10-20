# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import textwrap
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast

import bcrypt
import jwt

from opsml.cards import Card, ModelCard
from opsml.cards.project import ProjectCard
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import check_package_exists, clean_string
from opsml.registry.semver import (
    CardVersion,
    SemVerRegistryValidator,
    SemVerSymbols,
    SemVerUtils,
    VersionType,
)
from opsml.registry.sql.base.db_initializer import DBInitializer
from opsml.registry.sql.base.query_engine import (
    AuthQueryEngine,
    MessageQueryEngine,
    ProjectQueryEngine,
    RunQueryEngine,
    get_query_engine,
)
from opsml.registry.sql.base.registry_base import SQLRegistryBase
from opsml.registry.sql.base.sql_schema import SQLTableGetter
from opsml.registry.sql.base.utils import log_card_change
from opsml.registry.sql.connectors.connector import DefaultConnector
from opsml.scouter.integration import ScouterClient
from opsml.settings.config import config
from opsml.storage.client import StorageClient
from opsml.types import RegistryTableNames, RegistryType
from opsml.types.extra import Message, User

logger = ArtifactLogger.get_logger()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class ServerRegistry(SQLRegistryBase):
    """A registry that retrieves data from a database."""

    def __init__(self, registry_type: RegistryType, storage_client: StorageClient):
        super().__init__(registry_type, storage_client)

        connector = DefaultConnector(tracking_uri=config.opsml_tracking_uri).get_connector()
        tables = [t.value for t in RegistryTableNames if t.value != RegistryTableNames.BASE.value]
        db_initializer = DBInitializer(
            engine=connector.sql_engine,
            registry_tables=tables,
        )
        db_initializer.initialize()

        self.engine = get_query_engine(db_engine=db_initializer.engine, registry_type=registry_type)
        self._table = SQLTableGetter.get_table(table_name=self.table_name)
        self._scouter_client = ScouterClient()

    @property
    def registry_type(self) -> RegistryType:
        """Registry type"""
        raise NotImplementedError

    @staticmethod
    def validate(registry_name: str) -> bool:
        raise NotImplementedError

    @property
    def unique_repositories(self) -> Sequence[str]:
        """Returns a list of unique repositories"""
        return self.engine.get_unique_repositories(table=self._table)

    def query_stats(self, search_term: Optional[str] = None) -> Dict[str, int]:
        """Query stats from Card Database
        Args:
            search_term:
                Search term to filter by

        Returns:
            Dictionary of stats
        """
        return self.engine.query_stats(table=self._table, search_term=search_term)

    def query_page(
        self,
        sort_by: str,
        page: int,
        repository: Optional[str] = None,
        search_term: Optional[str] = None,
    ) -> List[List[Union[str, int]]]:
        """Query page from Card Database
        Args:
            sort_by:
                Field to sort by
            page:
                Page number
            repository:
                Repository to filter by
            search_term:
                Search term to filter by

        Returns:
            List of tuples
        """
        return cast(
            List[List[Union[str, int]]],
            self.engine.query_page(
                table=self._table,
                repository=repository,
                search_term=search_term,
                sort_by=sort_by,
                page=page,
            ),
        )

    def _get_versions_from_db(self, name: str, repository: str, version_to_search: Optional[str] = None) -> List[str]:
        """Query versions from Card Database

        Args:
            name:
                Card name
            repository:
                Card repository
            version_to_search:
                Version to search for
        Returns:
            List of versions
        """
        results = self.engine.get_versions(
            table=self._table,
            name=name,
            repository=repository,
            version=version_to_search,
        )

        if bool(results):
            versions = [result.version for result in results]
            return SemVerUtils.sort_semvers(versions=versions)
        return []

    def set_version(
        self,
        name: str,
        repository: str,
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
            repository:
                Card repository
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
            repository=repository,
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
        repository: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        max_date: Optional[str] = None,
        limit: Optional[int] = None,
        ignore_release_candidates: bool = False,
        query_terms: Optional[Dict[str, Any]] = None,
        sort_by_timestamp: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves records from registry

        Args:
            name:
                Artifact record name
            repository:
                Repository card is assigned to
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
            query_terms:
                Dictionary of query terms to filter by
            sort_by_timestamp:
                If True, sorts by timestamp descending


        Returns:
            Dictionary of records
        """

        cleaned_name = clean_string(name)
        cleaned_repository = clean_string(repository)

        records = self.engine.get_records_from_table(
            table=self._table,
            name=cleaned_name,
            repository=cleaned_repository,
            version=version,
            uid=uid,
            max_date=max_date,
            tags=tags,
            limit=limit,
            query_terms=query_terms,
            sort_by_timestamp=sort_by_timestamp,
        )

        # may not need
        # if cleaned_name is not None:
        # records = self._sort_by_version(records=records)

        if self._table.__tablename__ == RegistryTableNames.RUN.value:
            records = self._sort_by_timestamp(records=records)

        if version is not None:
            if ignore_release_candidates:
                records = [record for record in records if not SemVerUtils.is_release_candidate(record["version"])]
            if any(symbol in version for symbol in [SemVerSymbols.CARET, SemVerSymbols.TILDE]):
                # return top version
                return records[:1]

        if version is None and ignore_release_candidates:
            records = [record for record in records if not SemVerUtils.is_release_candidate(record["version"])]

        return records

    def check_uid(self, uid: str, registry_type: RegistryType) -> bool:
        result = self.engine.get_uid(
            uid=uid,
            table_to_check=RegistryTableNames[registry_type.value.upper()].value,
        )
        return bool(result)

    @log_card_change
    def delete_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Deletes a card record from the backend database"""
        self.engine.delete_card_record(table=self._table, card=card)
        return card, "deleted"


class ServerDataCardRegistry(ServerRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.DATA

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.DATA.value


class ServerModelCardRegistry(ServerRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.MODEL

    def _validate_datacard_uid(self, uid: str) -> None:
        exists = self.check_uid(uid=uid, registry_type=RegistryType.DATA)
        if not exists:
            raise ValueError("ModelCard must be associated with a valid DataCard uid")

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
            card = cast(ModelCard, card)

            if card.to_onnx:
                if not check_package_exists("onnx"):
                    raise ModuleNotFoundError(
                        """To convert a model to onnx, please install onnx via one of the extras
                        (opsml[sklearn_onnx], opsml[tf_onnx], opsml[torch_onnx]) or set to_onnx to False.
                        """
                    )

            if card.datacard_uid is not None:
                self._validate_datacard_uid(uid=card.datacard_uid)

            super().register_card(
                card=card,
                version_type=version_type,
                pre_tag=pre_tag,
                build_tag=build_tag,
            )

            # write profile to scouter
            if card.interface.drift_profile is not None and self._scouter_client.server_running is not None:
                try:
                    self._scouter_client.insert_drift_profile(
                        drift_profile=card.interface.drift_profile.model_dump_json(),
                        drift_type=card.interface.drift_profile.config.drift_type,
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    logger.error(f"Failed to insert drift profile: {exc}")

    def update_card(self, card: Card) -> None:
        """
        Update an artifact card based on current registry

        Args:
            card:
                Card to register
        """

        card = cast(ModelCard, card)

        if card.datacard_uid is not None:
            self._validate_datacard_uid(uid=card.datacard_uid)

        super().update_card(card)

        # write profile to scouter
        if card.interface.drift_profile is not None and self._scouter_client.server_running is not None:
            try:
                self._scouter_client.update_drift_profile(
                    repository=card.repository,
                    name=card.name,
                    version=card.version,
                    drift_profile=card.interface.drift_profile.model_dump_json(),
                    drift_type=card.interface.drift_profile.config.drift_type,
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.error(f"Failed to update drift profile: {exc}")

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.MODEL.value


class ServerRunCardRegistry(ServerRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.RUN

    def get_metric(
        self, run_uid: str, name: Optional[List[str]] = None, names_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get metric from run card

        Args:
            run_uid:
                run card uid
            name:
                List of names of metrics to retrieve
            names_only:
                if True, will return only names

        Returns:
            metrics

        """
        assert isinstance(self.engine, RunQueryEngine)

        return self.engine.get_metric(run_uid=run_uid, name=name, names_only=names_only)

    def get_hw_metric(self, run_uid: str) -> Optional[List[Dict[str, Any]]]:
        """Get hw metric

        Args:
            run_uid:
                run card uid

        Returns:
            metrics

        """
        assert isinstance(self.engine, RunQueryEngine)

        return self.engine.get_hw_metric(run_uid=run_uid)

    def insert_metric(self, metric: List[Dict[str, Any]]) -> None:
        """Insert metric into run card

        Args:
            metric:
                list of metric(s)
        """
        assert isinstance(self.engine, RunQueryEngine)

        self.engine.insert_metric(metric=metric)

    def insert_hw_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """Insert hardware metric into run card

        Args:
            metrics:
                hardware metrics
        """
        assert isinstance(self.engine, RunQueryEngine)

        self.engine.insert_hw_metrics(metrics=metrics)

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.RUN.value

    def get_parameter(self, run_uid: str, name: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get metric from run card
        Args:
            run_uid:
                run card uid
            name:
                List of names of parameters to retrieve
        Returns:
            metrics
        """
        assert isinstance(self.engine, RunQueryEngine)

        return self.engine.get_parameter(run_uid=run_uid, name=name)

    def insert_parameter(self, parameter: List[Dict[str, Any]]) -> None:
        """Insert parameter into run card
        Args:
            parameter:
                list of parameter(s)
        """
        assert isinstance(self.engine, RunQueryEngine)

        self.engine.insert_parameter(parameter=parameter)


class ServerPipelineCardRegistry(ServerRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.PIPELINE

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.PIPELINE.value

    def delete_card(self, card: Card) -> None:
        raise ValueError("PipelineCardRegistry does not support delete_card")


class ServerProjectCardRegistry(ServerRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.PROJECT

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.PROJECT.value

    def delete_card(self, card: Card) -> None:
        raise ValueError("ProjectCardRegistry does not support delete_card")

    def register_card(
        self,
        card: Card,
        version_type: VersionType = VersionType.MINOR,
        pre_tag: str = "rc",
        build_tag: str = "build",
    ) -> None:
        """Registers a ProjectCard to the registry"""
        card = cast(ProjectCard, card)

        # set project id on card even if its already registered
        card.project_id = self.get_project_id(project_name=card.name, repository=card.repository)

        # check if ProjectCard already exists
        record = self.list_cards(name=card.name, repository=card.repository, limit=1)
        if record:
            return None

        return super().register_card(card, version_type, pre_tag, build_tag)

    def get_project_id(self, project_name: str, repository: str) -> int:
        """get project id from project name and repository

        Args:
            project_name:
                project name
            repository:
                repository name

        Returns:
            project id

        """
        assert isinstance(self.engine, ProjectQueryEngine)

        return self.engine.get_project_id(
            project_name=project_name,
            repository=repository,
        )


class ServerAuditCardRegistry(ServerRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.AUDIT

    def validate_uid(self, uid: str, registry_type: RegistryType) -> bool:
        return self.check_uid(uid=uid, registry_type=registry_type)

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.AUDIT.value


class ServerAuthRegistry(ServerRegistry):
    @property
    def auth_db(self) -> AuthQueryEngine:
        assert isinstance(self.engine, AuthQueryEngine)
        return self.engine

    def get_user(self, username: str) -> Optional[User]:
        """Get user from auth db

        Args:
            username:
                username

        Returns:
            user

        """

        return self.auth_db.get_user(username=username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user from auth db

        Args:
            email:
                email

        Returns:
            user

        """

        return self.auth_db.get_user_by_email(email=email)

    def add_user(self, user: User) -> None:
        """Add user to auth db

        Args:
            user:
                user

        """

        self.auth_db.add_user(user=user)

    def authenticate_user(self, user: User, password: str) -> bool:
        """Authenticates user password

        Args:
            user:
                User object
            password:
                password

        Returns:
            user

        """

        # encoding user password
        user_bytes = password.encode("utf-8")
        assert isinstance(user.hashed_password, str)
        matched: bool = bcrypt.checkpw(user_bytes, user.hashed_password.encode("utf-8"))

        # checking password
        return matched

    def update_user(self, user: User) -> bool:
        """Update user

        Args:
            user:
                user

        """

        return self.auth_db.update_user(user=user)

    def delete_user(self, user: User) -> bool:
        """Delete user

        Args:
            user:
                user

        """

        return self.auth_db.delete_user(user)

    def create_access_token(self, user: User, minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
        """Creates a temporary access token for user"""
        expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)

        data = {
            "sub": user.username,
            "scopes": user.scopes.model_dump(),
            "exp": expire,
        }
        encoded_jwt: str = jwt.encode(data, config.opsml_jwt_secret, config.opsml_jwt_algorithm)
        return encoded_jwt

    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.AUTH

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.AUTH.value


class ServerMessageRegistry(ServerRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.MESSAGE

    @property
    def message_db(self) -> MessageQueryEngine:
        assert isinstance(self.engine, MessageQueryEngine)
        return self.engine

    def get_messages(self, registry: str, uid: str) -> List[Optional[Message]]:
        """Get messages from registry

        Args:
            registry:
                registry name
            uid:
                uid

        Returns:
            messages

        """
        assert isinstance(self.engine, MessageQueryEngine)
        return self.engine.get_messages(registry=registry, uid=uid)

    def insert_message(self, message: Message) -> None:
        """Add message to registry

        Args:
            message:
                message

        """
        assert isinstance(self.engine, MessageQueryEngine)

        self.engine.insert_message(message=message)

    def update_message(self, message: Message) -> None:
        """Update message in registry

        Args:
            message:
                message

        """
        assert isinstance(self.engine, MessageQueryEngine)

        self.engine.update_message(message=message)

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.MESSAGE.value

    def delete_card(self, card: Card) -> None:
        raise ValueError("MessageRegistry does not support delete_card")

    def register_card(
        self,
        card: Card,
        version_type: VersionType = VersionType.MINOR,
        pre_tag: str = "rc",
        build_tag: str = "build",
    ) -> None:
        raise ValueError("MessageRegistry does not support register_card")
