from unittest import result
from .data_model import SqlDataRegistrySchema
from sqlalchemy import select
import sqlalchemy


class SqlRegistry:
    def __init__(
        self,
        db_name: str,
        engine: sqlalchemy.engine.base.Engine,
    ):
        self.engine = engine
        self.schema = SqlDataRegistrySchema
        self.schema.__table_args__ = {"schema": f"{db_name}"}

    def list_data(self):
        sql_statement = select(self.schema.table_name).group_by(
            self.schema.table_name,
        )
        with self.engine.connect() as db_conn:
            results = db_conn.execute(sql_statement).fetchall()

            return [row.table_name for row in results]
