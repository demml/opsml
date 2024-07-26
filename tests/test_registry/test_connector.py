import pytest  # type: ignore

from opsml.registry.sql.connectors.base import BaseSQLConnection


def test_base_sql_connection():
    USER = "fake-user"
    PASSWORD = "fakepass"
    DB_NAME = "fake-db"
    CONNECTION_NAME = "test-project:us-central1:fake-instance"

    MYSQL_TRACKING_URI = f"mysql+pymysql://{USER}:{PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{CONNECTION_NAME}"
    with pytest.raises(NotImplementedError):
        BaseSQLConnection(tracking_uri=MYSQL_TRACKING_URI)
