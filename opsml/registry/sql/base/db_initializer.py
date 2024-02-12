# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import logging
import os
from pathlib import Path
from typing import List

try:
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    from sqlalchemy.engine.base import Engine
except ModuleNotFoundError as err:
    from opsml.helpers.utils import startup_import_error_message

    startup_import_error_message(err)

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.sql_schema import Base

# too much logging going on with alembic
logging.getLogger("alembic").propagate = False

logger = ArtifactLogger.get_logger()


DIR_PATH = Path(__file__).parents[1]


class DBInitializer:
    def __init__(self, engine: Engine, registry_tables: List[str]):
        self.engine = engine
        self.registry_tables = registry_tables

    def registry_tables_exist(self) -> bool:
        """Checks if all tables have been created previously"""
        table_names = inspect(self.engine).get_table_names()
        return all((expected_table in table_names for expected_table in self.registry_tables))

    def create_tables(self) -> None:
        """Creates tables"""
        logger.info("Creating database tables")

        tables = [Base.metadata.tables[table] for table in self.registry_tables]
        Base.metadata.create_all(self.engine, checkfirst=True, tables=tables)

    def update_tables(self) -> None:
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
