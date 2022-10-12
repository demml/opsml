import pytest
from opsml_data.helpers.defaults import defaults
from opsml_data.connector.data_model import SqlDataRegistrySchema
from opsml_data.connector import DataRegistry
import os


@pytest.fixture(scope="session")
def test_defaults():

    return defaults


@pytest.fixture(scope="session")
def db_name():
    return os.environ.get("DB_NAME")


@pytest.fixture(scope="session")
def db_username():
    return os.environ.get("DB_USERNAME")


@pytest.fixture(scope="session")
def db_password():
    return os.environ.get("DB_PASSWORD")


@pytest.fixture(scope="session")
def db_instance():
    return os.environ.get("DB_INSTANCE_NAME")


@pytest.fixture(scope="session")
def connection(
    test_defaults,
    db_instance,
    db_name,
    db_username,
    db_password,
):
    conn = DataRegistry(
        gcp_project=test_defaults.GCP_PROJECT,
        gcp_region=test_defaults.GCP_REGION,
        instance_name=db_instance,
        db_name=db_name,
        username=db_username,
        password=db_password,
    )

    return conn


def data_model():
    base = declarative_base()


class SqlDataRegistrySchema(base):
    __tablename__ = "data_registry"

    date = Column("date", String(100))
    timestamp = Column(
        "timestamp",
        FLOAT,
        primary_key=True,
    )
    table_name = Column("table_name", String(100))
    storage_uri = Column("storage_uri", String(100))
    feature_mapping = Column("feature_mapping", JSON)
    version = Column("version", Integer, nullable=False)

    __table_args__ = {"schema": "flight-plan-data-registry"}

    def __repr__(cls):
        return f"<SqlMetric({cls.__tablename__}"


@pytest.fixture(scope="session")
def setup_database(connection):

    schema = SqlDataRegistrySchema
    schema.__tablename__ = "test_data_registry"
    print(schema)
    schema.__table__.create(
        bind=connection.engine,
        checkfirst=True,
    )
    a
    yield

    # schema.__table__.drop(bind=connection.engine)
