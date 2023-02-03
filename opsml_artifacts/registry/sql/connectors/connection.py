from opsml_artifacts.registry.sql.connectors.local_connection import LocalSQLConnection
from opsml_artifacts.registry.sql.connectors.base_connection import BaseSQLConnection
from typing import Optional, Type

# we could loop through subclasses but I dont want to import them if not needed
class SQLConnector:
    @staticmethod
    def get_connector(connector_type: Optional[str] = None) -> Type[BaseSQLConnection]:
        if connector_type == "gcp":
            from opsml_artifacts.registry.sql.connectors.gcp_connection import CloudSQLConnection

            return CloudSQLConnection
        return LocalSQLConnection
