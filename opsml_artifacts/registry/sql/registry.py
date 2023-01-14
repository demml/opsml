import uuid
from typing import Any, Dict, Iterable, List, Optional, Type, Union, cast

import pandas as pd
from pyshipt_logging import ShiptLogging
from sqlalchemy import func, select
from sqlalchemy.sql import FromClause, Select
from sqlalchemy.sql.expression import ColumnElement

from opsml_artifacts.registry.cards.card import (
    DataCard,
    ExperimentCard,
    ModelCard,
    PipelineCard,
)
from opsml_artifacts.registry.sql.records import (
    DataRegistryRecord,
    LoadedDataRecord,
    LoadedExperimentRecord,
    LoadedModelRecord,
    LoadedPipelineRecord,
    PipelineRegistryRecord,
)
from opsml_artifacts.registry.sql.sql_schema import (
    REGISTRY_TABLES,
    ArtifactTableNames,
    Session,
    TableSchema,
    engine,
)

logger = ShiptLogging.get_logger(__name__)

ArtifactCardTypes = Union[ModelCard, DataCard, ExperimentCard, PipelineCard]

SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]


class QueryCreatorMixin:
    def _create_max_version_query(self, name: str, team: str, table: Type[REGISTRY_TABLES]):
        query = select(func.max(table.version))
        query = self._filter(query=query, field="name", value=name, table=table)
        query = self._filter(query=query, field="team", value=team, table=table)
        return query

    def _create_select_base(self, table: Type[REGISTRY_TABLES]) -> Select:
        sql_table = cast(SqlTableType, table)
        stmt: Select = select(sql_table)
        return stmt

    def _filter(
        self,
        query,
        field: str,
        value: Union[Optional[str], Optional[int]],
        table: Type[REGISTRY_TABLES],
    ):
        return query.filter(getattr(table, field) == value)

    def _get_version(self, query, table: Type[REGISTRY_TABLES], version: Optional[int] = None):
        if version is None:
            return query.order_by(table.version.desc())  # type: ignore
        return query.filter(table.version == version)

    def _create_record_query(
        self,
        table: Type[REGISTRY_TABLES],
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ):
        query = self._create_select_base(table=table)
        if bool(uid):
            return self._filter(query=query, field="uid", value=uid, table=table)

        if not any([name, team]):
            raise ValueError(
                """If no uid is supplied then name and team are required.
            Version can also be supplied with version and team."""
            )

        query = self._filter(query=query, field="name", value=name, table=table)
        query = self._filter(query=query, field="team", value=team, table=table)
        query = self._get_version(query=query, version=version, table=table)
        return query

    def _create_list_query(
        self,
        table: Type[REGISTRY_TABLES],
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
    ):
        query = self._create_select_base(table=table)

        if bool(uid):
            return self._filter(query=query, field="uid", value=uid, table=table)
        if name is not None:
            query = self._filter(query=query, field="name", value=name, table=table)
        if team is not None:
            query = self._filter(query=query, field="team", value=team, table=table)
        if version is not None:
            query = self._get_version(query=query, version=version, table=table)

        return query

    def _create_check_uid_exists(self, uid: str, table_to_check: str):

        table = TableSchema.get_table(table_name=table_to_check)
        query = select(table.uid)  # type: ignore
        sub_query = self._filter(query=query, field="uid", value=uid, table=table)
        query = select(table.uid).filter(sub_query.exist())  # type: ignore

        return query


class SQLRegistry(QueryCreatorMixin):
    def __init__(self, table_name: str):
        self._session = Session()
        self._table = TableSchema.get_table(table_name=table_name)
        self._create_table()
        self.supported_card = "anycard"
        self.table_name = self._table.__tablename__

    def _is_correct_card_type(self, card: ArtifactCardTypes):
        if self.supported_card.lower() != card.__class__.__name__.lower():
            return False
        return True

    def _create_table(self):
        self._table.__table__.create(bind=engine, checkfirst=True)

    def _set_uid(self):
        return uuid.uuid4().hex

    def _set_version(self, name: str, team: str) -> int:
        query = self._create_max_version_query(name=name, team=team, table=self._table)
        last = self._session.execute(query).scalar()
        return 1 + (last if last else 0)

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

        query = self._create_record_query(
            name=name,
            team=team,
            version=version,
            uid=uid,
            table=self._table,
        )

        return self._session.scalars(query).first()

    def _add_and_commit(self, record: Dict[str, Any]):
        self._session.add(self._table(**record))
        self._session.commit()
        logger.info(
            "Table: %s registered as version %s",
            record.get("name"),
            record.get("version"),
        )

    def _update_record(self, record: Dict[str, Any]):
        record_uid = record.get("uid")
        query = self._session.query(self._table).filter(self._table.uid == record_uid)
        query.update(record)
        self._session.commit()

        logger.info(
            "Data: %s, version:%s updated",
            record.get("name"),
            record.get("version"),
        )

    # Create
    def register_card(
        self,
        card: Any,
    ) -> None:
        """
        Adds new data record to data registry.
        Args:
            data_card (DataCard or RegistryRecord): DataCard to register. RegistryRecord is also accepted.
        """

        # check compatibility
        if not self._is_correct_card_type(card=card):
            raise ValueError(
                f"""Card of type {card.__class__.__name__} is not supported by
                registery {self._table.__tablename__}"""
            )

        version = self._set_version(name=card.name, team=card.team)
        record = card.create_registry_record(  # type: ignore
            registry_name=self._table.__tablename__,
            uid=self._set_uid(),
            version=version,
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

        query = self._create_list_query(
            table=self._table,
            uid=uid,
            name=name,
            team=team,
            version=version,
        )

        return pd.read_sql(query, self._session.bind)

    def _check_uid(self, uid: str, table_to_check: str):
        query = self._create_check_uid_exists(uid=uid, table_to_check=table_to_check)
        if not self._session.execute(query).scalar():
            return False
        return True

    def query_value_from_uid(self, uid: str, columns: List[str]) -> Dict[str, Any]:
        results = self._query_record(uid=uid)
        result_dict = results.__dict__
        return {col: result_dict[col] for col in columns}

    # Read
    def load_card(  # type: ignore
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> ArtifactCardTypes:
        """Loads data or model card"""
        raise NotImplementedError

    @staticmethod
    def validate(registry_name: str) -> bool:
        """Validate registry type"""

        return True


class DataCardRegistry(SQLRegistry):
    def __init__(self, table_name: str = "data"):
        super().__init__(table_name=table_name)
        self.supported_card = "datacard"

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
        loaded_record = LoadedDataRecord(**sql_data.__dict__)

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
        if registry_name in [
            ArtifactTableNames.TEST_DATA_REGISTRY.name,
            ArtifactTableNames.DATA_REGISTRY.name,
        ]:
            return True
        return False


class ModelCardRegistry(SQLRegistry):
    def __init__(self, table_name: str = "model"):
        super().__init__(table_name=table_name)
        self.supported_card = "modelcard"

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
        model_definition = model_record.load_model_card_definition()

        return ModelCard.parse_obj(model_definition)
        # registry = DataRegistryChecker(model_registry_name=model_registry_name)

    def _get_data_table_name(self) -> str:
        if ArtifactTableNames.TEST_MODEL_REGISTRY.name == self.table_name:
            return ArtifactTableNames.TEST_DATA_REGISTRY.name
        return ArtifactTableNames.DATA_REGISTRY.name

    def _validate_datacard_uid(self, uid: str) -> None:
        table_to_check = self._get_data_table_name()
        exists = self._check_uid(uid=uid, table_to_check=table_to_check)
        if not exists:
            raise ValueError("""ModelCard must be assoicated with a valid DataCard uid""")

    def _is_data_uid_none(self, uid: Optional[str]) -> bool:
        return bool(uid)

    # custom registration
    def register_card(self, card: ModelCard) -> None:

        if self._is_data_uid_none(uid=card.data_card_uid):
            raise ValueError("""ModelCard must be assoicated with a valid DataCard uid""")

        if card.data_card_uid is not None:
            self._validate_datacard_uid(uid=card.data_card_uid)

        return super().register_card(card)

    @staticmethod
    def validate(registry_name: str):
        if registry_name in [
            ArtifactTableNames.TEST_MODEL_REGISTRY.name,
            ArtifactTableNames.MODEL_REGISTRY.name,
        ]:
            return True
        return False


class ExperimentCardRegistry(SQLRegistry):
    def __init__(self, table_name: str = "experiment"):
        super().__init__(table_name=table_name)
        self.supported_card = "experimentcard"

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
        experiment_record.load_artifacts()
        return ExperimentCard(**experiment_record.dict())

    @staticmethod
    def validate(registry_name: str):
        if registry_name in [
            ArtifactTableNames.TEST_EXPERIMENT_REGISTRY.name,
            ArtifactTableNames.EXPERIMENT_REGISTRY.name,
        ]:
            return True
        return False


class PipelineCardRegistry(SQLRegistry):
    def __init__(self, table_name: str = "pipeline"):
        super().__init__(table_name=table_name)
        self.supported_card = "pipelinecard"

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


class CardRegistry:
    def __init__(self, registry_name: str):
        self.registry: SQLRegistry = self._set_registry(registry_name=registry_name)
        self.table_name = self.registry._table.__tablename__

    def _set_registry(self, registry_name: str) -> SQLRegistry:
        registry_name = ArtifactTableNames(registry_name.lower()).name
        registry = next(
            registry
            for registry in SQLRegistry.__subclasses__()
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

        return self.registry.list_cards(
            uid=uid,
            name=name,
            team=team,
            version=version,
        )

    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        uid: Optional[str] = None,
        version: Optional[int] = None,
    ) -> ArtifactCardTypes:

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

        return self.registry.load_card(
            uid=uid,
            name=name,
            team=team,
            version=version,
        )

    def register_card(
        self,
        card: ArtifactCardTypes,
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
        card: ArtifactCardTypes,
    ) -> None:
        """Update and artifact card (DataCard only) based on current registry

        Args:
            card (DataCard or ModelCard): Card to register

        Returns:
            None
        """

        if not hasattr(self.registry, "update_card"):
            raise ValueError(f"""{card.__class__.__name__} as no 'update_card' attribute""")

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
        return self.registry.query_value_from_uid(uid=uid, columns=columns)
