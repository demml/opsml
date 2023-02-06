from opsml_artifacts.registry.sql.connectors import LocalSQLConnection, CloudSQLConnection, SQLConnector
from opsml_artifacts.registry.sql.registry import CardRegistry
import pytest


def _test_local_connection():
    local_connection = LocalSQLConnection(db_file_path=":memory")
    local_connection.get_engine()


@pytest.mark.parametrize("load_secrets", [True, False])
def test_cloudsql_connection(load_secrets, mock_gcp_vars, mock_gcp_secrets):

    cloudsql_connection = CloudSQLConnection(
        load_from_secrets=load_secrets,
        db_type="mysql",
        **mock_gcp_vars,
    )
    cloudsql_connection.get_engine()


def test_card_registry_connection(mock_gcp_vars, mock_gcp_secrets):
    connector = SQLConnector.get_connector("gcp")
    client = connector(
        load_from_secrets=True,
        db_type="mysql",
        **mock_gcp_vars,
    )
    for i in ["pipeline", "model"]:
        registry = CardRegistry(registry_name=i, connection_client=client)
        registry.list_cards()
