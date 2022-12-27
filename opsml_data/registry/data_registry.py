from typing import List, Optional

import pandas as pd
from pyshipt_logging import ShiptLogging
from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker

from opsml_data.registry.connection import create_sql_engine
from opsml_data.registry.data_card import DataCard
from opsml_data.registry.models import RegistryRecord
from opsml_data.registry.sql_schema import DataSchema, TableSchema
from opsml_data.registry.storage import load_record_data_from_storage

logger = ShiptLogging.get_logger(__name__)

engine = create_sql_engine()
Session = sessionmaker(bind=engine)


class SQLRegistry:
    def __init__(self):
        self.session = Session()
        self.table = TableSchema.get_table(table_name="data_registry")

    def _set_version(
        self,
        data_name: str,
        team: str,
    ):
        last = (
            self.session.query(func.max(self.table.version))
            .filter(and_(self.table.data_name == data_name, self.table.team == team))
            .scalar()
        )
        return 1 + (last if last else 0)

    def _query_record(
        self,
        data_name: str,
        team: str,
        version: int = None,
    ) -> List[DataSchema]:

        query = self.session.query(self.table)
        query = query.filter(and_(self.table.data_name == data_name, self.table.team == team))

        if version is None:
            query = query.order_by(self.table.version.desc())

        else:
            query = query.filter(self.table.version == version)

        return query.all()[0]


class DataRegistry(SQLRegistry):

    # Create
    def register(self, data_card: DataCard) -> None:
        """
        Adds new data record to data registry.
        Args:
            data_card: Data card to register.
        """

        # version logic is sql based (should be kept in registry)
        data_card.version = self._set_version(data_name=data_card.data_name, team=data_card.team)

        # call private method for class
        datamodel = data_card.create_registry_metadata(version=data_card.version)  # pylint: disable=protected-access

        self.session.add(self.table(**datamodel.dict()))
        self.session.commit()
        logger.info(
            "Table: %s registered as version %s",
            data_card.data_name,
            data_card.version,
        )

    # Read
    def list_data(
        self,
        data_name: str = None,
        team: str = None,
        version: int = None,
    ) -> pd.DataFrame:

        """Retrieves records for data registry

        Args:
            data_name (str): Optional name of table
            team (str): Optional name of data science team

        Returns:
            pandas dataframe of data records
        """

        query = self.session.query(self.table)

        if data_name is not None:
            query = query.filter(self.table.data_name == data_name)

        if team is not None:
            query = query.filter(self.table.team == team)

        if version is not None:
            query = query.filter(self.table.version == version)

        return pd.read_sql(query.statement, query.session.bind)

    # Read
    def load(
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

        sql_data: DataSchema = self._query_record(
            data_name=data_name,
            team=team,
            version=version,
        )

        # load data
        data = load_record_data_from_storage(
            storage_uri=sql_data.data_uri,
            data_type=sql_data.data_type,
        )

        if sql_data.drift_uri is not None:
            drift_report = load_record_data_from_storage(
                storage_uri=sql_data.drift_uri,
                data_type="DataFrame",
            )
        else:
            drift_report = None

        data_card = DataCard(
            data=data,
            drift_report=drift_report,
            uid=sql_data.uid,
            date=sql_data.date,
            timestamp=sql_data.timestamp,
            app_env=sql_data.app_env,
            data_name=sql_data.data_name,
            team=sql_data.team,
            data_uri=sql_data.data_uri,
            drift_uri=sql_data.drift_uri,
            feature_map=sql_data.feature_map,
            data_splits=sql_data.data_splits,
            data_type=sql_data.data_type,
            version=sql_data.version,
            user_email=sql_data.user_email,
        )

        return data_card

    def update(self, data_card: DataCard) -> None:

        """Updates an existing data card

        Args:
            data_card (DataCard): Existing data card record

        Returns:
            None
        """

        metadata = RegistryRecord(
            data_name=data_card.data_name,
            team=data_card.team,
            data_uri=data_card.data_uri,
            drift_uri=data_card.drift_uri,
            feature_map=data_card.feature_map,
            data_type=data_card.data_type,
            data_splits=data_card.data_splits,
            version=data_card.version,
            user_email=data_card.user_email,
            uid=data_card.uid,
        )

        self.session.query(self.table).filter(self.table.uid == metadata.uid).update(
            metadata.dict(),
        )
        self.session.commit()
        logger.info(
            "Data: %s, version:%s updated",
            data_card.data_name,
            data_card.version,
        )
