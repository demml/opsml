from opsml_data.registry.connection import create_sql_engine


def test_connection():
    engine = create_sql_engine()
