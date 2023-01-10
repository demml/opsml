import uuid
from typing import Any, Dict, Optional, Type, Union, cast

import pandas as pd
from pyshipt_logging import ShiptLogging
from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker

from opsml_data.registry.cards.card import ArtifactCard, DataCard, ModelCard
from opsml_data.registry.cards.connection import create_sql_engine
from opsml_data.registry.cards.record_models import (
    ArtifactRegistryTables,
    DataRegistryRecord,
    LoadedDataRecord,
    LoadedModelRecord,
    ModelRegistryRecord,
    ValidCards,
)
from opsml_data.registry.cards.sql_schema import TableSchema

logger = ShiptLogging.get_logger(__name__)

engine = create_sql_engine()
Session = sessionmaker(bind=engine)


class SQLRegistry:
    def __init__(self, table_name: str):
        self._session = Session()
        self._table = TableSchema.get_table(table_name=table_name)
        self._create_table()

    def _create_table(self):
        self._table.__table__.create(bind=engine, checkfirst=True)

    def _set_uid(self):
        return uuid.uuid4().hex

    def _set_version(self, name: str, team: str) -> int:

        last = (
            self._session.query(func.max(self._table.version))
            .filter(and_(self._table.name == name, self._table.team == team))
            .scalar()
        )
        return 1 + (last if last else 0)

    def _query_record(
        self,
        name: str,
        team: str,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ):

        query = self._session.query(self._table)

        if bool(uid):
            query = query.filter(self._table.uid == uid)
            return query.all()[0]

        query = query.filter(and_(self._table.name == name, self._table.team == team))

        if version is None:
            query = query.order_by(self._table.version.desc())

        else:
            query = query.filter(self._table.version == version)

        return query.all()[0]

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
        card: Union[DataCard, ModelCard],
    ) -> None:
        """
        Adds new data record to data registry.
        Args:
            data_card (DataCard or RegistryRecord): DataCard to register. RegistryRecord is also accepted.
        """

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

        query = self._session.query(self._table)

        if bool(uid):
            query.filter(self._table.uid == uid)
            return pd.read_sql(query.statement, self._session.bind)

        if name is not None:
            query = query.filter(self._table.name == name)

        if team is not None:
            query = query.filter(self._table.team == team)

        if version is not None:
            query = query.filter(self._table.version == version)

        return pd.read_sql(query.statement, self._session.bind)

    # Read
    def load_card(  # type: ignore
        self,
        name: str,
        team: str,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> Union[ModelCard, DataCard]:
        """Loads data or model card"""

    @staticmethod
    def validate(registry_name: str) -> bool:
        """Validate registry type"""

        return True


class DataCardRegistry(SQLRegistry):
    def __init__(self, table_name: str = "data_registry"):
        super().__init__(table_name=table_name)

    # specific loading logic
    def load_card(
        self,
        name: str,
        team: str,
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

        sql_data = self._query_record(
            name=name,
            team=team,
            version=version,
            uid=uid,
        )

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
        if "data_registry" in registry_name:
            return True
        return False


class ModelCardRegistry(SQLRegistry):
    def __init__(self, table_name: str = "model_registry"):
        super().__init__(table_name=table_name)

    # specific loading logic
    def load_card(
        self,
        name: str,
        team: str,
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

    @staticmethod
    def validate(registry_name: str):
        if "model_registry" in registry_name:
            return True
        return False


class CardRegistry:
    def __init__(self, registry_name: str):
        self.registry: SQLRegistry = self.set_registry(registry_name=registry_name)

    def set_registry(self, registry_name: str) -> SQLRegistry:
        registry_name = ArtifactRegistryTables(registry_name).name.lower()

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
            uid (str): Unique identifier for DataCard. If present, the uid takes precedence.


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
        name: str,
        team: str,
        uid: Optional[str] = None,
        version: Optional[int] = None,
    ) -> Union[DataCard, ModelCard]:

        """Loads a specific card

        Args:
            name (str): Card name
            team (str): Team associated with card
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

    def _validate_card(self, card: Union[ModelCard, DataCard]):
        if "data" in self.registry._table.__tablename__:  # pylint: disable=protected-access
            if ValidCards("data").name.lower() != card.__class__.__name__.lower():
                raise ValueError("Data registry only supports DataCard")
        else:
            if ValidCards("model").name.lower() != card.__class__.__name__.lower():
                raise ValueError("Model registry only supports ModelCard")

    def register_card(
        self,
        card: Union[ModelCard, DataCard],
    ) -> None:
        """Register an artifact card (DataCard or ModelCard) based on current registry

        Args:
            card (DataCard or ModelCard): Card to register

        Returns:
            None
        """

        self._validate_card(card=card)
        self.registry.register_card(card=card)

    def update_card(
        self,
        card: Union[ModelCard, DataCard],
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
