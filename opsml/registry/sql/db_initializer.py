# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Any, List

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.sql_schema import Base

logger = ArtifactLogger.get_logger()

DIR_PATH = os.path.dirname(__file__)


class DBInitializer:
    def __init__(self, engine, registry_tables: List[Any]):
        self.engine = engine
        self.registry_tables = registry_tables

    def registry_tables_exist(self) -> bool:
        """Checks if all tables have been created previously"""
        table_names = inspect(self.engine).get_table_names()
        registry_tables = self.registry_tables
        return all(registry_table.value in table_names for registry_table in registry_tables)

    def create_tables(self):
        """Creates tables"""
        logger.info("Creating database tables")
        Base.metadata.create_all(self.engine)

    def update_tables(self):
        """Updates tables in db based on alembic revisions"""

        # credit to mlflow for this implementation
        db_url = str(self.engine.url)

        config = self.get_alembic_config(db_url=db_url)
        with self.engine.begin() as connection:
            config.attributes["connection"] = connection  # pylint: disable=unsupported-assignment-operation
            command.upgrade(config, "heads")

    def get_alembic_config(self, db_url: str) -> Config:
        alembic_dir = os.path.join(DIR_PATH, "migration")
        db_url = db_url.replace("%", "%%")
        config = Config(os.path.join(alembic_dir, "alembic.ini"))
        config.set_main_option("sqlalchemy.url", db_url)
        config.set_main_option("script_location", f"{alembic_dir}/alembic")
        config.attributes["configure_logger"] = False  # pylint: disable=unsupported-assignment-operation

        return config

    def initialize(self) -> None:
        """Create tables if they don't exist and update"""
        if not self.registry_tables_exist():
            self.create_tables()
        self.update_tables()
