"""add compute environment to runcard registry

Revision ID: 29b9f009e99a
Revises: c54a9fbab8dc
Create Date: 2024-08-28 13:03:49.430373

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.sql_schema import RegistryTableNames
from opsml.types import CommonKwargs

logger = ArtifactLogger.get_logger()


# revision identifiers, used by Alembic.
revision: str = "29b9f009e99a"
down_revision: Union[str, None] = "c54a9fbab8dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    logger.info("Alembic revision: Adding compute environment to run registry - {}", revision)
    try:
        bind = op.get_context().bind
        insp = sa.inspect(bind)

        assert insp is not None

        table_name = RegistryTableNames.from_str("run")
        columns = insp.get_columns(table_name)

        if "compute_environment" not in [col["name"] for col in columns]:
            op.add_column(
                table_name,
                sa.Column(
                    "compute_environment",
                    sa.JSON,
                    nullable=True,
                ),
            )

    except Exception as e:
        logger.error("Error adding columns: {}", e)
        raise e


def downgrade() -> None:
    logger.info("Alembic downgrade: {}", revision)

    try:
        bind = op.get_context().bind
        insp = sa.inspect(bind)

        assert insp is not None

        table_name = RegistryTableNames.from_str("run")
        op.drop_column(table_name, "compute_environment")

    except Exception as e:
        logger.error("Error adding columns: {}", e)
        raise e
