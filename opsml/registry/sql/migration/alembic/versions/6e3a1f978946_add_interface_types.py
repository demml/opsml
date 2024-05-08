"""Add interface types

Revision ID: 6e3a1f978946
Revises: 
Create Date: 2024-05-02 10:44:58.659238

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.sql_schema import RegistryTableNames
from opsml.types import CommonKwargs

logger = ArtifactLogger.get_logger()


# revision identifiers, used by Alembic.
revision: str = "6e3a1f978946"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    logger.info("Alembic revision: Adding types to model and data registries - {}", revision)
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
