import uuid
from typing import Any, Dict, Optional, Union

import pandas as pd
from pyshipt_logging import ShiptLogging
from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker

from opsml_data.registry.connection import create_sql_engine
from opsml_data.registry.data_card import DataCard
from opsml_data.registry.models import LoadedRecord, RegistryRecord
from opsml_data.registry.sql_schema import TableSchema

logger = ShiptLogging.get_logger(__name__)

engine = create_sql_engine()
Session = sessionmaker(bind=engine)


class SQLRegistry:
    def __init__(self, table_name: str = "data_registry"):
        self._session = Session()
        self._table = TableSchema.get_table(table_name=table_name)
        self._create_table()

    def _create_table(self):
        self._table.__table__.create(bind=engine, checkfirst=True)

    def _set_uid(self):
        return uuid.uuid4().hex

    def _set_version(self, data_name: str, team: str) -> int:

        last = (
            self._session.query(func.max(self._table.version))
            .filter(and_(self._table.data_name == data_name, self._table.team == team))
            .scalar()
        )
        return 1 + (last if last else 0)

    def _query_record(
        self,
        data_name: str,
        team: str,
        version: Optional[int] = None,
    ):

        query = self._session.query(self._table)
        query = query.filter(and_(self._table.data_name == data_name, self._table.team == team))

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
            record.get("data_name"),
            record.get("version"),
        )

    def _update_record(self, record: Dict[str, Any]):
        record_uid = record.get("uid")
        query = self._session.query(self._table).filter(self._table.uid == record_uid)
        query.update(record)
        self._session.commit()

        logger.info(
            "Data: %s, version:%s updated",
            record.get("data_name"),
            record.get("version"),
        )


class DataRegistry(SQLRegistry):

    # Create
    def register_data(self, data_card: Union[DataCard, RegistryRecord]) -> None:
        """
        Adds new data record to data registry.
        Args:
            data_card (DataCard or RegistryRecord): DataCard to register. RegistryRecord is also accepted.
        """
        if isinstance(data_card, DataCard):
            version = self._set_version(data_name=data_card.data_name, team=data_card.team)
            record = data_card.create_registry_record(
                data_registry=self._table.__tablename__,
                uid=self._set_uid(),
                version=version,
            )
        else:
            record = data_card

        self._add_and_commit(record=record.dict())

    # Read
    def list_data(
        self,
        data_name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
    ) -> pd.DataFrame:

        """Retrieves records for data registry

        Args:
            data_name (str): Optional name of table
            team (str): Optional name of data science team

        Returns:
            pandas dataframe of data records
        """

        query = self._session.query(self._table)

        if data_name is not None:
            query = query.filter(self._table.data_name == data_name)

        if team is not None:
            query = query.filter(self._table.team == team)

        if version is not None:
            query = query.filter(self._table.version == version)

        return pd.read_sql(query.statement, self._session.bind)

    # Read
    def load_data(
        self,
        data_name: str,
        team: str,
        version: Optional[int] = None,
    ) -> DataCard:

        """Loads a data card from the data registry

        Args:
            data_name (str): Data record name
            team (str): Team data is assigned to
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used

        Returns:
            Data card
        """

        sql_data = self._query_record(
            data_name=data_name,
            team=team,
            version=version,
        )
        loaded_record = LoadedRecord(**sql_data.__dict__)

        return DataCard(**loaded_record.dict())

    def update_data(self, data_card: DataCard) -> None:

        """Updates an existing data card in the data registry

        Args:
            data_card (DataCard): Existing data card record

        Returns:
            None
        """

        record = RegistryRecord(**data_card.dict())
        self._update_record(record=record.dict())
