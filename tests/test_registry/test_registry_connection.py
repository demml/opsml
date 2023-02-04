from opsml_artifacts.registry.sql.connectors import SQLConnector, CloudSQLConnection, LocalSQLConnection
from opsml_artifacts.registry.sql.registry import CardRegistry


def test_cloud_sql():
    connection = CloudSQLConnection(
        load_from_secrets=True,
        db_type="mysql",
    )
    connection.get_engine()


def test_local_sql():
    connection = LocalSQLConnection()
    connection.get_engine()


def test_connector_getter():
    connector = SQLConnector.get_connector("gcp")
    connector(
        load_from_secrets=True,
        db_type="mysql",
    ).get_engine()

    local_connector = SQLConnector.get_connector()
    local_connector().get_engine()


def test_card_registry_connection():
    connector = SQLConnector.get_connector("gcp")
    client = connector(load_from_secrets=True, db_type="mysql")
    for i in ["pipeline", "model"]:
        registry = CardRegistry(registry_name=i, connection_client=client)
        registry.list_cards()

    connector = SQLConnector.get_connector()
    client = connector()
    for i in ["pipeline", "model"]:
        registry = CardRegistry(registry_name=i, connection_client=client)
