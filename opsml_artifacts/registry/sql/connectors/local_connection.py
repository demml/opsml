from opsml_artifacts.registry.sql.connectors.base_connection import BaseSQLConnection
from typing import Optional
import os
import sqlalchemy


class LocalSQLConnection(BaseSQLConnection):
    """Connection string to pass to the registry for establishing
    a connection to a SQLite database

    Args:
        db_file_path (str): Optional file path to sqlite database, If no path is provided, a
        new database named "opsml_artifacts.db" will be created in the home user directory.
        If the "opsml_artifacts.db" already exists, a connection will be re-established (the
        database will not be overwritten)
    Returns:
        Instantiated class with required SQLite arguments
    """

    db_file_path: Optional[str]

    def _get_db_path(self):
        if not bool(self.db_file_path):
            return f"{os.path.expanduser('~')}/opsml_artifacts.db"
        return self.db_file_path

    def _set_sqlalchemy_url(self):
        return "sqlite://"

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        url = self._set_sqlalchemy_url()
        file_path = self._get_db_path()
        execution_options = {"schema_translate_map": {"ds-artifact-registry": None}}
        engine = sqlalchemy.create_engine(f"{url}/{file_path}", execution_options=execution_options)
        return engine
