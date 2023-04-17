from opsml.helpers.settings import DefaultConnector
from opsml.registry.sql.connectors.base import CloudSQLConnection


def test_cloudsql_parsing():
    USER = "fake-user"
    PASSWORD = "fakepass"
    DB_NAME = "fake-db"
    CONNECTION_NAME = "test-project:us-central1:fake-instance"

    MYSQL_TRACKING_URI = f"mysql+pymysql://{USER}:{PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{CONNECTION_NAME}"
    conn = DefaultConnector(tracking_uri=MYSQL_TRACKING_URI).get_connector()

    assert "CloudSqlMySql" in conn.__class__.__name__

    POSTGRES_TRACKING_URI = f"postgresql+psycopg2://{USER}:{PASSWORD}@/{DB_NAME}?host=/cloudsql/{CONNECTION_NAME}"
    conn = DefaultConnector(tracking_uri=POSTGRES_TRACKING_URI).get_connector()

    assert "CloudSqlPostgresql" in conn.__class__.__name__


def test_cloudsql():
    USER = "fake-user"
    PASSWORD = "fakepass"
    DB_NAME = "fake-db"
    CONNECTION_NAME = "test-project:us-central1:fake-instance"

    MYSQL_TRACKING_URI = f"mysql+pymysql://{USER}:{PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{CONNECTION_NAME}"
    CloudSQLConnection(tracking_uri=MYSQL_TRACKING_URI)
