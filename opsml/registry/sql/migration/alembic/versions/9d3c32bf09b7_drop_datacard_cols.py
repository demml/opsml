"""drop datacard cols

Revision ID: 9d3c32bf09b7
Revises: 094eabfc3ce8
Create Date: 2023-04-26 02:10:42.996340

"""
import os
from enum import Enum

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

# revision identifiers, used by Alembic.
revision = "9d3c32bf09b7"
down_revision = "094eabfc3ce8"
branch_labels = None
depends_on = None

DATACARD_NAME = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")


class DropCols(str, Enum):
    DATA_SPLITS = "data_splits"
    FEATURE_MAOE = "feature_map"
    FEATURE_DESCRIPTIONS = "feature_descriptions"
    ADDITIONAL_INFO = "additional_info"
    DEPENDENT_VARS = "dependent_vars"


def upgrade() -> None:
    """Drop feature columns from registry table"""

    logger.info("Dropping DataCard feature columns from registry")
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind=bind)
    columns = insp.get_columns(DATACARD_NAME)

    for drop_col in DropCols:
        if any(column.get("name") == drop_col.value for column in columns):
            op.drop_column(
                table_name=DATACARD_NAME,
                column_name=drop_col.value,
            )


def downgrade() -> None:
    pass
