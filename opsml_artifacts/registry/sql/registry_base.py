import uuid
from typing import Any, Dict, Iterable, Optional, Union, cast

import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import ColumnElement, FromClause

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.helpers.models import ApiRoutes
from opsml_artifacts.registry.cards.cards import (
    DataCard,
    ExperimentCard,
    ModelCard,
    PipelineCard,
)
from opsml_artifacts.registry.cards.types import ArtifactCardProto
from opsml_artifacts.registry.sql.models import SaveInfo
from opsml_artifacts.registry.sql.query_helpers import QueryCreator
from opsml_artifacts.registry.sql.sql_schema import TableSchema

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
        self.supported_card = f"{table_name.split('_')[1]}Card"
        self.storage_client = settings.storage_client
        self._table = TableSchema.get_table(table_name=table_name)

    def _get_session(self):
        raise NotImplementedError

    def _increment_version(self, version: str, version_type: str) -> str:
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
            raise KeyError(
                f"""f{version_type} is not a recognized sem_var type.
            Valid types are "major", "minor", and "patch". {error}
            """
            ) from error

        version_splits[version_idx] = str(int(version_splits[version_idx]) + 1)
        for idx in range(len(sem_var_map.keys())):
            if idx > version_idx:
                version_splits[idx] = str(0)

        return ".".join(version_splits)

    def _set_version(self, name: str, team: str, version_type: str) -> str:
        raise NotImplementedError

    def _is_correct_card_type(self, card: ArtifactCardProto):
        """Checks wether the current card is associated with the correct registry type"""
        return self.supported_card.lower() == card.__class__.__name__.lower()

    def _get_uid(self) -> str:
        """Sets a unique id to be applied to a card"""
        return uuid.uuid4().hex

    def _query_record(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
    ):
        raise NotImplementedError

    def _add_and_commit(self, record: Dict[str, Any]):
        raise NotImplementedError

    def _update_record(self, record: Dict[str, Any]):
        raise NotImplementedError

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
            - this prefix is already inferred using either "OPSML_TRACKING_URL" or "OPSML_STORAGE_URL"
            env variables. In addition, save_path should specify a directory.
        """

        # check compatibility
        if not self._is_correct_card_type(card=card):
            raise ValueError(
                f"""Card of type {card.__class__.__name__} is not supported by registery
                {self._table.__tablename__}"""
            )

        if self._check_uid(uid=str(card.uid), table_to_check=self.table_name):
            raise ValueError(
                """This Card has already been registered.
            If the card has been modified try upating the Card in the registry.
            If registering a new Card, create a new Card of the correct type.
            """
            )

        # need to find way to compare previous cards and automatically
        # determine if change is major or minor
        version = self._set_version(
            name=card.name,
            team=card.team,
            version_type=version_type,
        )

        if save_path is None:
            save_path = f"{self.table_name}/{card.team}/{card.name}/v-{version}"

        record = card.create_registry_record(
            save_info=SaveInfo(
                blob_path=save_path,
                name=card.name,
                team=card.team,
                version=version,
                storage_client=self.storage_client,
            ),
            uid=self._get_uid(),
        )

        self._add_and_commit(record=record.dict())

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def _check_uid(self, uid: str, table_to_check: str):
        raise NotImplementedError

    def load_card(  # type: ignore
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
    ) -> CardTypes:
        raise NotImplementedError


class SQLRegistry(SQLRegistryBase):
    def __init__(self, table_name: str):
        super().__init__(table_name)

        self._engine = self._get_engine()
        self._session = self._get_session()
        self._create_table_if_not_exists()
        self.table_name = self._table.__tablename__

    def _get_engine(self):
        return settings.connection_client.get_engine()

    def _get_session(self):
        """Sets the sqlalchemy session to be used for all queries"""
        session = sessionmaker(bind=self._engine)
        return session

    def _create_table_if_not_exists(self):
        self._table.__table__.create(bind=self._engine, checkfirst=True)

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

        if bool(result):
            return self._increment_version(
                version=result.version,
                version_type=version_type,
            )
        return "1.0.0"

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

        if result is not None:
            result = cast(Dict[str, Any], result.__dict__)

        return result

    def _add_and_commit(self, record: Dict[str, Any]):
        sql_record = self._table(**record)

        with self._session() as sess:
            sess.add(sql_record)
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

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
    ) -> pd.DataFrame:

        """Retrieves records from registry

        Args:
            name (str): Artifact record name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.


        Returns:
            Dictionary of records
        """

        query = query_creator.record_from_table_query(
            table=self._table,
            name=name,
            team=team,
            version=version,
            uid=uid,
        )

        results_list = []
        with self._session() as sess:
            results = sess.execute(query).all()

        for row in results:
            result_dict = row[0].__dict__
            result_dict.pop("_sa_instance_state")
            results_list.append(result_dict)

        return pd.DataFrame(results_list)

    def _check_uid(self, uid: str, table_to_check: str):
        query = query_creator.uid_exists_query(
            uid=uid,
            table_to_check=table_to_check,
        )
        with self._session() as sess:
            result = sess.scalars(query).first()
        return bool(result)

    # Read
    def load_card(  # type: ignore
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
    ) -> CardTypes:
        """Loads data or model card"""
        raise NotImplementedError


# work in progress
class SQLRegistryAPI(SQLRegistryBase):
    def __init__(self, table_name: str):
        super().__init__(table_name)

        self._session = self._get_session()
        self._api_url = settings.opsml_tacking_url

    def _get_session(self):
        """Gets the requests session for connecting to the opsml api"""
        return settings.request_client

    def _check_uid(self, uid: str, table_to_check: str):

        data = self._session.post_request(
            url=f"{self._api_url}/{ApiRoutes.CHECK_UID.value}",
            json={"uid": uid, "table_name": self.table_name},
        )

        if bool(data.get("uid_exists")):
            raise ValueError(
                """This Card has already been registered.
            If the card has been modified try upating the Card in the registry.
            If registering a new Card, create a new Card of the correct type.
            """
            )

    def _set_version(self, name: str, team: str, version_type: str = "minor") -> str:
        data = self._session.post_request(
            url=f"{self._api_url}/{ApiRoutes.SET_VERSION.value}",
            json={
                "name": name,
                "team": team,
                "version_type": version_type,
                "table_name": self.table_name,
            },
        )
        return data.get("version")

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
    ) -> pd.DataFrame:

        """Retrieves records from registry

        Args:
            name (str): Artifact record name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.


        Returns:
            Dictionary of records
        """
        data = self._session.post_request(
            url=f"{self._api_url}/{ApiRoutes.LIST_CARDS.value}",
            json={
                "name": name,
                "team": team,
                "version": version,
                "uid": uid,
                "table_name": self.table_name,
            },
        )

        return pd.DataFrame.from_records(data)

    def _add_and_commit(self, record: Dict[str, Any]):
        data = self._session.post_request(
            url=f"{self._api_url}/{ApiRoutes.ADD_RECORD.value}",
            json={
                "record": record,
                "table_name": self.table_name,
            },
        )

        if bool(data.get("registered")):
            logger.info(
                "%s: %s, version:%s registered",
                self._table.__tablename__,
                record.get("name"),
                record.get("version"),
            )

    def _update_record(self, record: Dict[str, Any]):
        data = self._session.post_request(
            url=f"{self._api_url}/{ApiRoutes.UPDATE_RECORD.value}",
            json={
                "record": record,
                "table_name": self.table_name,
            },
        )

        if bool(data.get("updated")):
            logger.info(
                "%s: %s, version:%s updated",
                self._table.__tablename__,
                record.get("name"),
                record.get("version"),
            )

    def _query_record(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
    ):
        data = self._session.post_request(
            url=f"{self._api_url}/{ApiRoutes.QUERY_RECORD.value}",
            json={
                "name": name,
                "team": team,
                "version": version,
                "uid": uid,
                "table_name": self.table_name,
            },
        )

        return data.get("record")


# mypy isnt good with dynamic class creation
def get_sql_registry_base() -> Any:
    if settings.request_client is not None:
        return cast(Any, SQLRegistryAPI)
    return cast(Any, SQLRegistry)


Registry = get_sql_registry_base()
