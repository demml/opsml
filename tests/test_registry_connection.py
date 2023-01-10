from opsml_artifacts.registry.cards.connection import create_sql_engine


def test_connection():
    engine = create_sql_engine()
