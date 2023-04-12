from unittest.mock import patch, MagicMock
from opsml_artifacts.registry.sql.connectors.connector import LocalSQLConnection
from opsml_artifacts.registry.sql.migration.migrate import run_alembic
from sqlalchemy.engine.reflection import Inspector


def test_migrations(mock_local_engine, experiment_table_to_migrate):

    with patch.multiple(
        "opsml_artifacts.registry.sql.connectors.connector.LocalSQLConnection",
        get_engine=MagicMock(return_value=mock_local_engine),
    ) as engine_mock:

        local_client = LocalSQLConnection(tracking_uri="sqlite://")
        engine = local_client.get_engine()

        experiment_table_to_migrate.__table__.create(bind=engine, checkfirst=True)

        run_alembic()

        inspector = Inspector.from_engine(engine)
        tables = inspector.get_table_names()

        assert "OPSML_EXPERIMENT_REGISTRY" not in tables
