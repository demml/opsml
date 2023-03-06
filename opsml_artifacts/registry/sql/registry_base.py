import uuid
from typing import Any, Dict, Iterable, Optional, Union, cast
import requests
from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import ColumnElement, FromClause

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.cards import (
    DataCard,
    ExperimentCard,
    ModelCard,
    PipelineCard,
)
from opsml_artifacts.registry.cards.types import ArtifactCardProto
from opsml_artifacts.registry.sql.query_helpers import QueryCreator


from opsml_artifacts.registry.sql.sql_schema import TableSchema
from opsml_artifacts.helpers.settings import settings

logger = ArtifactLogger.get_logger(__name__)


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]
CardTypes = Union[ExperimentCard, ModelCard, DataCard, PipelineCard]


sem_var_map = {
    "major": 0,
    "minor": 1,
    "patch": 2,
}

query_creator = QueryCreator()


class SQLRegistryBase:
    def __init__(self, table_name: str):
        """Base class for SQL Registries to inherit from

        Args:
            table_name (str): CardRegistry table name
        """
        self.table_name = table_name
        self.supported_card = f"{table_name.split('_')[0]}Card"
        self.storage_client = settings.storage_client

    def _get_session(self):
        raise NotImplementedError

    def _increment_version(
        self,
        version: str,
        version_type: str,
    ) -> str:
        """Increments a version based on version type

        Args:
            version (str): Current version
            version_type (str): Type of version increment. Accepted

        Returns:
            New version string
        """

        version_splits = version.split(".")

        try:
            version_idx = sem_var_map[version_type.lower()]
        except KeyError as error:
            raise ValueError(
                f"""f{version_type} is not a recognized sem_var type.
            Valid types are "major", "minor", and "patch".
            """
            )

        version_splits[version_idx] = str(int(version_splits[version_idx]) + 1)
        for idx in range(len(sem_var_map.keys())):
            if idx > version_idx:
                version_splits[idx] = str(0)

        return ".".join(version_splits)

    def _set_version(self, name: str, team: str) -> int:
        raise NotImplementedError

    def _is_correct_card_type(self, card: ArtifactCardProto):
        """Checks wether the current card is associated with the correct registry type"""
        return self.supported_card.lower() == card.__class__.__name__.lower()

    def _set_uid(self):
        """Sets a unique id to be applied to a card"""
        return uuid.uuid4().hex

    def _query_record(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ):
        raise NotImplementedError

    def _add_and_commit(self, record: Dict[str, Any]):
        raise NotImplementedError

    def _update_record(self, record: Dict[str, Any]):
        raise NotImplementedError

    def register_card(self, card: ArtifactCardProto) -> None:
        raise NotImplementedError

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def _check_uid(self, uid: str, table_to_check: str):
        raise NotImplementedError

    def load_card(  # type: ignore
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> CardTypes:
        raise NotImplementedError


class SQLRegistry(SQLRegistryBase):
    def __init__(self, table_name: str):
        super().__init__(table_name)

        self._engine = self._get_engine()
        self._session = self._get_session()
        self._table = TableSchema.get_table(table_name=table_name)
        self._create_table_if_not_exists()
        self.table_name = self._table.__tablename__

    def _get_engine(self):
        return create_engine(settings.opsml_tacking_url)

    def _get_session(self):
        """Sets the sqlalchemy session to be used for all queries"""
        session = sessionmaker(bind=self.engine)
        return session

    def _create_table_if_not_exists(self):
        self._table.__table__.create(bind=self.engine, checkfirst=True)

    def _set_version(self, name: str, team: str, version_type: str) -> str:
        """Sets a version following semantic version standards

        Args:
            name (str): Card name
            team (str): Team card belongs to
            version_type (str): Type of version increment. Accepted
            values are "major", "minor" and "patch

        Returns:
            Version string
        """

        query = query_creator.create_version_query(
            table=self._table,
            name=name,
            team=team,
        )

        with self._session() as sess:
            result = sess.scalars(query).first()

        return self._increment_version(
            version=result.version,
            version_type=version_type,
        )

    def _query_record(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
    ):

        """Creates and executes a query to pull a given record based on
        name, team, version, or uid
        """

        query = query_creator.record_from_table_query(
            table=self._table,
            name=name,
            team=team,
            version=version,
            uid=uid,
        )

        with self._session() as sess:
            result = sess.scalars(query).first()

        return result

    def _add_and_commit(self, record: Dict[str, Any]):
        record = self._table(**record)

        with self._session() as sess:
            sess.add(record)
            sess.commit()

        logger.info(
            "%s: %s registered as version %s",
            self._table.__tablename__,
            record.get("name"),
            record.get("version"),
        )

    def _update_record(self, record: Dict[str, Any]):
        record_uid = cast(str, record.get("uid"))

        with self._session() as sess:
            query = sess.query(self._table).filter(self._table.uid == record_uid)
            query.update(record)
            sess.commit()

        logger.info(
            "%s: %s, version:%s updated",
            self._table.__tablename__,
            record.get("name"),
            record.get("version"),
        )

    def register_card(self, card: ArtifactCardProto) -> None:
        """
        Adds new record to registry.
        Args:
            data_card (DataCard or RegistryRecord): DataCard to register. RegistryRecord is also accepted.
        """

        # check compatibility
        if not self._is_correct_card_type(card=card):
            raise ValueError(
                f"""Card of type {card.__class__.__name__} is not supported by registery {self._table.__tablename__}"""
            )

        if self._check_uid(uid=str(card.uid), table_to_check=self.table_name):
            raise ValueError(
                """This Card has already been registered.
            If the card has been modified try upating the Card in the registry.
            If registering a new Card, create a new Card of the correct type.
            """
            )

        version = self._set_version(name=card.name, team=card.team)

        record = card.create_registry_record(
            registry_name=self.table_name,
            uid=self._set_uid(),
            version=version,
            storage_client=self.storage_client,
        )

        with self._session() as sess:
            sess.add(record.dict())
            sess.commit()

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
    ) -> Dict[str, Any]:

        """Retrieves records from registry

        Args:
            name (str): Artifact ecord name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.


        Returns:
            Dictionary of records
        """

        query = self._list_records_from_table(table=self._table, uid=uid, name=name, team=team, version=version)
        result = self._execute_query(query=query)
        return result.__dict__

    def _check_uid(self, uid: str, table_to_check: str):
        query = self._query_if_uid_exists(uid=uid, table_to_check=table_to_check)
        exists = self._get_first(query=query)
        return bool(exists)

    # Read
    def load_card(  # type: ignore
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> CardTypes:
        """Loads data or model card"""
        raise NotImplementedError

    @staticmethod
    def validate(registry_name: str) -> bool:
        """Validate registry type"""

        raise NotImplementedError
