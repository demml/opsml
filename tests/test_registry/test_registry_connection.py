from opsml_artifacts.registry.sql.connection import create_sql_engine


def test_connection():
    engine = create_sql_engine()
