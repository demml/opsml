from opsml.registry.utils.settings import DefaultConnector
from opsml.registry.sql.connectors.base import CloudSQLConnection, BaseSQLConnection
import sqlalchemy
import pytest
from google.cloud.sql.connector import IPTypes


def test_cloudsql_mysql_parsing():
    USER = "fake-user"
    PASSWORD = "fakepass"
    DB_NAME = "fake-db"
    CONNECTION_NAME = "test-project:us-central1:fake-instance"

    MYSQL_TRACKING_URI = f"mysql+pymysql://{USER}:{PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{CONNECTION_NAME}"
    conn = DefaultConnector(tracking_uri=MYSQL_TRACKING_URI).get_connector()

    # these should work
    assert conn._ip_type == IPTypes.PUBLIC.value
    assert isinstance(conn._connection_name, str)
    assert conn._conn is not None
    assert isinstance(conn.sql_engine, sqlalchemy.engine.base.Engine)

    assert "CloudSqlMySql" in conn.__class__.__name__


def test_cloudsql_postgres_parsing():
    USER = "fake-user"
    PASSWORD = "fakepass"
    DB_NAME = "fake-db"
    CONNECTION_NAME = "test-project:us-central1:fake-instance"
    POSTGRES_TRACKING_URI = f"postgresql+psycopg2://{USER}:{PASSWORD}@/{DB_NAME}?host=/cloudsql/{CONNECTION_NAME}"
    conn = DefaultConnector(tracking_uri=POSTGRES_TRACKING_URI).get_connector()

    # these should work
    assert conn._ip_type == IPTypes.PUBLIC.value
    assert isinstance(conn._connection_name, str)
    assert conn._conn is not None
    assert isinstance(conn.sql_engine, sqlalchemy.engine.base.Engine)

    assert "CloudSqlPostgresql" in conn.__class__.__name__


def test_cloudsql():
    USER = "fake-user"
    PASSWORD = "fakepass"
    DB_NAME = "fake-db"
    CONNECTION_NAME = "test-project:us-central1:fake-instance"

    MYSQL_TRACKING_URI = f"mysql+pymysql://{USER}:{PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{CONNECTION_NAME}"
    with pytest.raises(NotImplementedError):
        conn = CloudSQLConnection(tracking_uri=MYSQL_TRACKING_URI)


def test_base_sql_connection():
    USER = "fake-user"
    PASSWORD = "fakepass"
    DB_NAME = "fake-db"
    CONNECTION_NAME = "test-project:us-central1:fake-instance"

    MYSQL_TRACKING_URI = f"mysql+pymysql://{USER}:{PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{CONNECTION_NAME}"
    with pytest.raises(NotImplementedError):
        conn = BaseSQLConnection(tracking_uri=MYSQL_TRACKING_URI)
