"""update tables

Revision ID: c54a9fbab8dc
Revises: 
Create Date: 2023-04-11 23:07:56.160420

"""

import sqlalchemy as sa
from alembic import op

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.sql_schema import RegistryTableNames
from opsml.types import CommonKwargs

logger = ArtifactLogger.get_logger()
# revision identifiers, used by Alembic.
revision = "c54a9fbab8dc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    logger.info("Alembic revision: Adding interface columns to model and data registries - {}", revision)
    try:
        bind = op.get_context().bind
        insp = sa.inspect(bind)

        assert insp is not None

        for table in ["model", "data"]:
            table_name = RegistryTableNames.from_str(table)
            columns = insp.get_columns(table_name)

            if "interface_type" not in [col["name"] for col in columns]:
                op.add_column(
                    table_name,
                    sa.Column(
                        "interface_type",
                        sa.String(64),
                        nullable=False,
                        server_default=CommonKwargs.UNDEFINED.value,
                    ),
                )

            if table == "model":
                if "task_type" not in [col["name"] for col in columns]:
                    op.add_column(
                        table_name,
                        sa.Column(
                            "task_type",
                            sa.String(64),
                            nullable=False,
                            server_default=CommonKwargs.UNDEFINED.value,
                        ),
                    )
    except Exception as e:
        logger.error("Error adding columns: {}", e)
        raise e


def downgrade() -> None:

    logger.info("Alembic revision: Removing types from model and data registries - {}", revision)

    try:
        bind = op.get_context().bind
        insp = sa.inspect(bind)

        assert insp is not None

        for table in ["model", "data"]:
            table_name = RegistryTableNames.from_str(table)
            columns = insp.get_columns(table_name)

            if "interface_type" in [col["name"] for col in columns]:
                op.drop_column(table_name, "interface_type")

            if table == "model":
                if "task_type" in [col["name"] for col in columns]:
                    op.drop_column(table_name, "task_type")
    except Exception as e:
        logger.error("Error dropping columns: {}", e)
        raise e
