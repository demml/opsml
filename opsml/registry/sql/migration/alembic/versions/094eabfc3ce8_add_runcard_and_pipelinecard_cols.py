"""add runcard and pipelinecard cols

Revision ID: 094eabfc3ce8
Revises: fd32b1afafd5
Create Date: 2023-04-23 19:30:22.774935

"""
import os
from enum import Enum

import sqlalchemy as inspect
from alembic import op
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.engine.reflection import Inspector

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

# repeating enum here so no imports from library
class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "OPSML_MODEL_REGISTRY")


class AddCols(str, Enum):
    RUNCARD_UID = "runcard_uid"
    PIPELINECARD_UID = "pipelinecard_uid"


sql_schema = {
    AddCols.RUNCARD_UID: Column("runcard_uid", String(2048)),
    AddCols.PIPELINECARD_UID: Column("pipelinecard_uid", String(2048)),
}


# revision identifiers, used by Alembic.
revision = "094eabfc3ce8"
down_revision = "fd32b1afafd5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Adds new columns for DataCards and ModelCards"""

    logger.info("Running runcard_uids and pipelinecard_uid revision")
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind=bind)

    for table_name in RegistryTableNames:
        columns = insp.get_columns(table_name.value)

        for add_col in AddCols:
            if not any(column.get("name") == add_col.value for column in columns):
                op.add_column(
                    table_name=table_name,
                    column=sql_schema[table_name],
                )


def downgrade() -> None:
    pass
