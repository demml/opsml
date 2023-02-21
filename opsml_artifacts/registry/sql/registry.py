import uuid
from typing import Any, Dict, Iterable, List, Optional, Union, cast

import pandas as pd
from sqlalchemy.engine.base import Engine
from sqlalchemy.sql.expression import ColumnElement, FromClause

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.cards import (
    DataCard,
    ExperimentCard,
    ModelCard,
    PipelineCard,
)
from opsml_artifacts.registry.cards.storage_system import StorageClientGetter
from opsml_artifacts.registry.cards.types import ArtifactCardProto
from opsml_artifacts.registry.sql.connectors import SQLConnector, SqlConnectorType
from opsml_artifacts.registry.sql.query import QueryCreatorMixin
from opsml_artifacts.registry.sql.records import (
    DataRegistryRecord,
    ExperimentRegistryRecord,
    LoadedDataRecord,
    LoadedExperimentRecord,
    LoadedModelRecord,
    LoadedPipelineRecord,
    PipelineRegistryRecord,
)
from opsml_artifacts.registry.sql.sql_schema import RegistryTableNames, SqlManager

logger = ArtifactLogger.get_logger(__name__)


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]
CardTypes = Union[ExperimentCard, ModelCard, DataCard, PipelineCard]


class SQLRegistry(QueryCreatorMixin, SqlManager):
    def __init__(
        self,
        table_name: str,
        engine: Engine,
        connection_args: Dict[str, Any],
    ):
        super().__init__(table_name=table_name, engine=engine)
        self.supported_card = f"{table_name.split('_')[0]}Card"

        # Get backend storage system to save artifacts to
        # Not sure how I feel about this: Registry is only losely coupled with storing artifacts
        # An artifact only knows which storage system to use based on Registry connection args
        self.storage_client = StorageClientGetter.get_storage_client(
            connection_args=connection_args,
        )

    def _is_correct_card_type(self, card: ArtifactCardProto):
        return self.supported_card.lower() == card.__class__.__name__.lower()

    def _set_uid(self):
        return uuid.uuid4().hex

    def _set_version(self, name: str, team: str) -> int:
        query = self._query_record_from_table(table=self._table, name=name, team=team)
        last = self._exceute_query(query)
        return 1 + (last.version if last else 0)

    def _query_record(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ):

        """Creates and executes a query to pull a given record based on
        name, team, version, or uid
        """
        query = self._query_record_from_table(name=name, team=team, version=version, uid=uid, table=self._table)
        return self._exceute_query(query=query)

    def _add_and_commit(self, record: Dict[str, Any]):
        self._add_commit_transaction(record=self._table(**record))
        logger.info(
            "%s: %s registered as version %s",
            self._table.__tablename__,
            record.get("name"),
            record.get("version"),
        )

    def _update_record(self, record: Dict[str, Any]):
        record_uid = cast(str, record.get("uid"))
        self._update_record_transaction(table=self._table, record_uid=record_uid, record=record)
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

        self._add_and_commit(record=record.dict())

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
    ) -> pd.DataFrame:

        """Retrieves records from registry

        Args:
            name (str): Artifact ecord name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.


        Returns:
            pandas dataframe of records
        """

        query = self._list_records_from_table(table=self._table, uid=uid, name=name, team=team, version=version)
        return pd.read_sql(query, self._session().bind)

    def _check_uid(self, uid: str, table_to_check: str):
        query = self._query_if_uid_exists(uid=uid, table_to_check=table_to_check)
        exists = self._exceute_query(query=query)
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


class DataCardRegistry(SQLRegistry):
    # specific loading logic
    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> DataCard:

        """Loads a data card from the data registry

        Args:
            name (str): Data record name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.

        Returns:
            DataCard
        """

        sql_data = self._query_record(name=name, team=team, version=version, uid=uid)
        loaded_record = LoadedDataRecord(
            **{
                **sql_data.__dict__,
                **{"storage_client": self.storage_client},
            }
        )

        return DataCard(**loaded_record.dict())

    # specific update logic
    def update_card(self, card: DataCard) -> None:

        """Updates an existing data card in the data registry

        Args:
            data_card (DataCard): Existing data card record

        Returns:
            None
        """

        record = DataRegistryRecord(**card.dict())
        self._update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.DATA


class ModelCardRegistry(SQLRegistry):
    # specific loading logic
    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> ModelCard:
        """Loads a data card from the data registry

        Args:
            name (str): Card name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used

        Returns:
            Data card
        """

        sql_data = self._query_record(name=name, team=team, version=version, uid=uid)
        model_record = LoadedModelRecord(**sql_data.__dict__)
        model_record.storage_client = self.storage_client
        modelcard_definition = model_record.load_model_card_definition()

        model_card = ModelCard.parse_obj(
            {
                **model_record.dict(),
                **modelcard_definition,
            }
        )
        return model_card

    def _get_data_table_name(self) -> str:
        return RegistryTableNames.DATA.value

    def _validate_datacard_uid(self, uid: str) -> None:
        table_to_check = self._get_data_table_name()
        exists = self._check_uid(uid=uid, table_to_check=table_to_check)
        if not exists:
            raise ValueError("""ModelCard must be assoicated with a valid DataCard uid""")

    def _has_data_card_uid(self, uid: Optional[str]) -> bool:
        return bool(uid)

    # custom registration
    def register_card(self, card: ArtifactCardProto) -> None:

        model_card = cast(ModelCard, card)

        if not self._has_data_card_uid(uid=model_card.data_card_uid):
            raise ValueError("""ModelCard must be assoicated with a valid DataCard uid""")

        if model_card.data_card_uid is not None:
            self._validate_datacard_uid(uid=model_card.data_card_uid)

        return super().register_card(card)

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.MODEL


class ExperimentCardRegistry(SQLRegistry):
    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> ExperimentCard:

        """Loads a data card from the data registry

        Args:
            name (str): Card name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used

        Returns:
            Data card
        """

        sql_data = self._query_record(name=name, team=team, version=version, uid=uid)
        experiment_record = LoadedExperimentRecord(**sql_data.__dict__)
        experiment_record.storage_client = self.storage_client
        experiment_record.load_artifacts()
        return ExperimentCard(**experiment_record.dict())

    def update_card(self, card: ExperimentCard) -> None:

        """Updates an existing pipeline card in the pipeline registry

        Args:
            card (PipelineCard): Existing pipeline card

        Returns:
            None
        """

        record = ExperimentRegistryRecord(**card.dict())
        self._update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.EXPERIMENT


class PipelineCardRegistry(SQLRegistry):
    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> PipelineCard:

        """Loads a PipelineCard from the pipeline registry

        Args:
            name (str): Card name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used

        Returns:
            PipelineCard
        """

        sql_data = self._query_record(name=name, team=team, version=version, uid=uid)
        pipeline_record = LoadedPipelineRecord(**sql_data.__dict__)
        return PipelineCard(**pipeline_record.dict())

    def update_card(self, card: PipelineCard) -> None:

        """Updates an existing pipeline card in the pipeline registry

        Args:
            card (PipelineCard): Existing pipeline card

        Returns:
            None
        """

        record = PipelineRegistryRecord(**card.dict())
        self._update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.PIPELINE


# CardRegistry also needs to set a storage file system
class CardRegistry:
    def __init__(
        self,
        registry_name: str,
        connection_client: Optional[SqlConnectorType] = None,
        connection_type: Optional[str] = None,
    ):

        """Interface for connecting to any of the ArtifactCard registries

        Args:
            registry_name (str): Name of the registry to connect to. Options are
            "pipeline", "model", "data" and "experiment".
            connection_client (Type[BaseSQLConnection]): Optional connection client for
            connecting to a SQL database. See list of connectors for available options.
            connection_type (str): Type of connection client to create. This is used for
            when you wish to call a connection client without having to specify the
            "connection_client" arg. For this arg, it is assumed you have the appropriate env
            variables set for the connection_type that is specified.

        Returns:
            Instantiated connection to specific Card registry

        Example:

            # With connection type
            cloud_sql = CloudSQLConnection(...)
            data_registry = CardRegistry(registry_name="data", connection_client=cloud_sql)

            # With connection client
            data_registry = CardRegistry(registry_name="data", connection_type="gcp")

        """
        self._validate_connection_args(
            connection_type=connection_type,
            connection_client=connection_client,
        )

        self.registry: SQLRegistry = self._set_registry(
            registry_name=registry_name,
            connection_client=connection_client,
            connection_type=connection_type,
        )

        self.table_name = self.registry._table.__tablename__

    def _validate_connection_args(
        self,
        connection_client: Optional[SqlConnectorType] = None,
        connection_type: Optional[str] = None,
    ) -> Optional[str]:

        """Checks if a connection client or type was passed. Returns "local" if neither was specified

        Args:
            connection_client (Type[BaseSQLConnection]): Connection subclass
            connection_type (str): Type of connection

        Returns
            "local" or None

        """
        if not any([bool(connection_client), bool(connection_type)]):
            logger.info("No connection args provided. Defaulting to local registry")
            return "local"
        return None

    def _get_connection(self, connection_type: str) -> SqlConnectorType:
        """Loads a subclass of BaseSQLConnection given a connection type

        Args:
            connection_type (str): Connection type

        Returns:
            SQL onnection client
        """

        connector = SQLConnector.get_connector(
            connector_type=connection_type,
        )

        if connection_type == "gcp":
            kwargs = {"load_from_secrets": True}
        else:
            kwargs = {}

        return cast(SqlConnectorType, connector(**kwargs))

    def _set_registry(
        self,
        registry_name: str,
        connection_client: Optional[SqlConnectorType] = None,
        connection_type: Optional[str] = None,
    ) -> SQLRegistry:

        """Returns a SQL registry to be used to register Cards

        Args:
            registry_name (str): Name of the registry (pipeline, model, data, experiment)
            connection_client (Type[BaseSQLConnection]): Optional SQL connection
            connection_type (str): Optional name of connection type

        Returns:
            SQL Registry
        """

        registry_name = RegistryTableNames[registry_name.upper()].value

        if not bool(connection_client):
            connection_client = self._get_connection(connection_type=str(connection_type))

        registry = next(
            registry
            for registry in SQLRegistry.__subclasses__()
            if registry.validate(
                registry_name=registry_name,
            )
        )

        connection_client = cast(SqlConnectorType, connection_client)

        return registry(
            table_name=registry_name,
            engine=connection_client.get_engine(),
            connection_args=connection_client.dict(),
        )

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
    ) -> pd.DataFrame:

        """Retrieves records from registry

        Args:
            name (str): Card name
            team (str): Team associated with card
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for Card. If present, the uid takes precedence.


        Returns:
            pandas dataframe of records
        """
        if name is not None:
            name = name.lower()

        if team is not None:
            team = team.lower()

        return self.registry.list_cards(uid=uid, name=name, team=team, version=version)

    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        uid: Optional[str] = None,
        version: Optional[int] = None,
    ) -> CardTypes:

        """Loads a specific card

        Args:
            name (str): Optional Card name
            team (str): Optional team associated with card
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.

        Returns
            ModelCard or DataCard
        """
        if name is not None:
            name = name.lower()

        if team is not None:
            team = team.lower()

        return self.registry.load_card(uid=uid, name=name, team=team, version=version)

    def register_card(
        self,
        card: ArtifactCardProto,
    ) -> None:
        """Register an artifact card (DataCard or ModelCard) based on current registry

        Args:
            card (DataCard or ModelCard): Card to register

        Returns:
            None
        """
        self.registry.register_card(card=card)

    def update_card(
        self,
        card: CardTypes,
    ) -> None:
        """Update and artifact card (DataCard only) based on current registry

        Args:
            card (DataCard or ModelCard): Card to register

        Returns:
            None
        """

        if not hasattr(self.registry, "update_card"):
            raise ValueError(f"""{card.__class__.__name__} has no 'update_card' attribute""")

        self.registry = cast(DataCardRegistry, self.registry)
        card = cast(DataCard, card)
        return self.registry.update_card(card=card)

    def query_value_from_card(self, uid: str, columns: List[str]) -> Dict[str, Any]:
        """Query column values from a specific Card

        Args:
            uid (str): Uid of Card
            columns (List[str]): List of columns to query

        Returns:
            Dictionary of column, values pairs
        """
        results = self.registry._query_record(uid=uid)  # pylint: disable=protected-access
        result_dict = results.__dict__
        return {col: result_dict[col] for col in columns}
