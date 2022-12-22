from opsml_data.registry.connection import create_sql_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func
from opsml_data.registry.sql_schema import TableSchema, DataSchema
from opsml_data.registry.data_model import (
    RegisterMetadata,
    DataStoragePath,
    RegisterMetadata,
    ArrowTable,
    DataArtifacts,
)
from opsml_data.registry.data_card import DataCard
from opsml_data.registry.data_writer import DataStorage
from typing import Union, List
import pandas as pd
import numpy as np
from opsml_data.registry.formatter import DataFormatter
import pyarrow as pa
from pyshipt_logging import ShiptLogging
from typing import Union, Optional
import pyarrow as pa
import numpy as np
import pandas as pd
import uuid

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

    def _query_data(
        self,
        data_name: str,
        team: str,
        version: int = None,
    ) -> List[DataSchema]:

        query = self.session.query(self.table.storage_uri)
        query = query.filter(and_(self.table.data_name == data_name, self.table.team == team))

        if version is None:
            query = query.order_by(self.table.version.desc())

        else:
            query = query.filter(self.table.version == version)

        return query.all()


class DataRegistry(SQLRegistry):
    def _convert_and_save(
        self,
        data: Union[pd.DataFrame, pa.Table, np.ndarray],
        data_name: str,
        version: int,
        team: str,
    ) -> ArrowTable:

        """Converts data into a pyarrow table or numpy array.

        Args:
            data (pd.DataFrame, pa.Table, np.array): Data to convert
            data_name (str): Name for data
            version (int): version of the data
            team (str): Name of team

        Returns:
            ArrowTable containing metadata
        """

        data: ArrowTable = DataFormatter.convert_data_to_arrow(data)
        data.feature_map = DataFormatter.create_table_schema(data.table)
        storage_path = DataStorage.save(data=data.table, data_name=data_name, version=version, team=team)
        data.storage_uri = storage_path.gcs_uri

        return data

    # Create
    def register(self, data_card: DataCard) -> RegisterMetadata:
        """
        Adds new data record to data registry.
        Args:
            data_name: Name of table. If table name is same as an existing table,
            a new version will be created.
            user_email: Email associated with this data.
            team: Data Science team assoiated with data.
            data: A pandas dataframe or numpy array.
        """

        version = self._set_version(data_name=data_card.data_name, team=data_card.team)

        data_artifact = self._convert_and_save(
            data=data_card.data,
            data_name=data_card.data_name,
            version=version,
            team=data_card.team,
        )

        if data_card.drift_report is not None:
            drift_artifact: ArrowTable = self._convert_and_save(data=data_card.drift_report)
            drift_uri = drift_artifact.storage_uri
        else:
            drift_uri = None

        datamodel = RegisterMetadata(
            data_name=data_card.data_name,
            team=data_card.team,
            data_uri=data_artifact.storage_uri,
            drift_uri=drift_uri,
            feature_map=data_artifact.feature_map,
            data_type=data_artifact.table_type,
            version=version,
            user_email=data_card.user_email,
        )

        self.session.add(self.table(**datamodel.dict()))
        self.session.commit()

        logger.info(
            "Table: %s registered as version %s",
            data_card.data_name,
            version,
        )

        return datamodel

    def list_data(
        self,
        data_name: str = None,
        team: str = None,
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

        return pd.read_sql(query.statement, query.session.bind)

    def load(
        self,
        data_name: str,
        team: str,
        version: int = None,
    ) -> DataCard:

        sql_data: DataSchema = self._query_data(
            data_name=data_name,
            team=team,
            version=version,
        )[0]

        # load data
        data = DataStorage.load(
            storage_uri=sql_data.data_uri,
            data_type=sql_data.data_type,
        )

        if sql_data.drift_uri is not None:
            drift_report = DataStorage.load(
                storage_uri=sql_data.drift_uri,
                data_type="DataFrame",
            )
        else:
            drift_report = None

        data_card = DataCard(
            data_name=sql_data.data_name,
            team=sql_data.team,
            user_email=sql_data.user_email,
            data=data,
            drift_report=drift_report,
            uid=sql_data.uid,
        )

        return data_card
