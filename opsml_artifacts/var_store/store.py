from enum import Enum
from typing import List, Optional

import pandas as pd

from opsml_data.connector.snowflake import SnowflakeQueryRunner
from opsml_data.helpers.utils import FindPath
from opsml_data.var_store.variables import DependentVariables


class VarStoreTables(str, Enum):
    OPSML_FP_ORDERS_TIME_ACTUALS = "order"
    OPSML_FP_BUNDLES_TIME_ACTUALS = "bundle"
    OPSML_FP_STOPS_DROP_OFF_TIME = "stop"


class VarStoreIdCol(str, Enum):
    NG_ORDER_ID = "order"
    TIME_BUNDLE_ID = "bundle"


class SQLGetter:
    @staticmethod
    def open_sql_file(filename: str) -> str:
        sql_path = FindPath().find_filepath(filename)

        with open(sql_path, "r", encoding="utf-8") as sql:
            sql_string = sql.read()
        return sql_string


class DependentVarQuery:
    def __init__(
        self,
        query: str,
        id_col: str,
        table: str,
        dependent_vars: DependentVariables,
    ):
        self.query = query
        self.table = table
        self.id_col = id_col
        self.dependent_vars = dependent_vars

    def create_query(self) -> str:
        query = f"""
            WITH USER_QUERY AS ({self.query})

            SELECT A.*,
            {','.join(self.dependent_vars.column_names)},
            {','.join(self.dependent_vars.eval_flgs)},
            {','.join(self.dependent_vars.eval_outlier)}
            FROM USER_QUERY AS A
            LEFT JOIN DATA_SCIENCE.{self.table} AS B
                ON A.{self.id_col} = B.{self.id_col}
            """
        return query


class DependentVarStore:
    def __init__(
        self,
        level: str,
        dependent_vars: List[str],
        query: Optional[str] = None,
        sql_file: Optional[str] = None,
    ):

        if query is not None:
            self.query = query

        if sql_file is not None:
            self.query = SQLGetter.open_sql_file(filename=sql_file)

        self.table = self.get_table(level=level)
        self.dependent_vars = self.parse_dependent_vars(
            level=level,
            dependent_vars=dependent_vars,
        )
        self.id_col = self.get_id_col(level=level)

    def get_id_col(self, level: str) -> str:
        if level == "stop":
            level = "bundle"

        return VarStoreIdCol(level).name

    def get_table(self, level: str) -> str:
        return VarStoreTables(level).name

    def parse_dependent_vars(
        self,
        level: str,
        dependent_vars: List[str],
    ) -> DependentVariables:

        return DependentVariables(
            level=level,
            dependent_vars=dependent_vars,
        )

    def get_query(self):
        return DependentVarQuery(**self.__dict__).create_query()

    def pull_data(self) -> pd.DataFrame:
        query = self.get_query()
        dataframe = SnowflakeQueryRunner(on_vpn=True).query_to_dataframe(query=query)

        return dataframe
