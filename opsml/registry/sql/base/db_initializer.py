# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import logging
import os
from pathlib import Path
from typing import List, Optional

try:
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    from sqlalchemy.engine.base import Engine
except ModuleNotFoundError as err:
    from opsml.helpers.utils import startup_import_error_message

    startup_import_error_message(err)

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.query_engine import AuthQueryEngine
from opsml.registry.sql.base.sql_schema import Base
from opsml.settings.config import config
from opsml.types.extra import User, UserScope

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

        alembic_config = self.get_alembic_config(db_url=db_url)
        with self.engine.begin() as connection:
            alembic_config.attributes["connection"] = connection  # pylint: disable=unsupported-assignment-operation
            command.upgrade(alembic_config, "heads")

    def get_alembic_config(self, db_url: str) -> Config:
        alembic_dir = os.path.join(DIR_PATH, "migration")
        db_url = db_url.replace("%", "%%")
        alembic_config = Config(os.path.join(alembic_dir, "alembic.ini"))
        alembic_config.set_main_option("sqlalchemy.url", db_url)
        alembic_config.set_main_option("script_location", f"{alembic_dir}/alembic")
        alembic_config.attributes["configure_logger"] = False  # pylint: disable=unsupported-assignment-operation

        return alembic_config

    def check_admin_user(self, username: str) -> None:
        """Check if admin user exists in auth db"""

        auth_engine = AuthQueryEngine(engine=self.engine)
        user: Optional[User] = auth_engine.get_user(username)

        if user is None:
            logger.info("Admin user does not exist. Creating...")
            auth_engine.add_user(
                User(
                    username=config.opsml_username,
                    password=config.opsml_password,
                    is_active=True,
                    scopes=UserScope(admin=True),
                )
            )

    def initialize(self) -> None:
        """Create tables if they don't exist and update"""

        if not self.registry_tables_exist():
            self.create_tables()
        self.update_tables()

        # check if admin username and pass exist in auth db
        if config.opsml_auth:
            assert config.opsml_username is not None, "Admin username must be set when using auth"
            assert config.opsml_password is not None, "Admin password must be set when using auth"
            self.check_admin_user(config.opsml_username)
