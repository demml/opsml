"""remove uris

Revision ID: 182bb743681e
Revises: 5b477729d615
Create Date: 2023-12-21 15:01:36.577762

"""
import sqlalchemy as sa
from alembic import op

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.types import RegistryTableNames

logger = ArtifactLogger.get_logger()


# revision identifiers, used by Alembic.
revision = "182bb743681e"
down_revision = "5b477729d615"
branch_labels = None
depends_on = None


def upgrade() -> None:
    logger.info("Alembic revision: Removing URIs - {}", revision)

    bind = op.get_context().bind
    insp = sa.inspect(bind)

    # model table cleanup
    table_name = RegistryTableNames.MODEL.value
    columns = insp.get_columns(table_name)

    for column in columns:
        if column["name"] in [
            "modelcard_uri",
            "trained_model_uri",
            "model_metadata_uri",
            "sample_data_uri",
        ]:
            logger.info("Dropping {} column from {} table", column["name"], table_name)
            with op.batch_alter_table(table_name) as batch_op:
                batch_op.drop_column(column["name"])

    # data table cleanup
    table_name = RegistryTableNames.DATA.value
    columns = insp.get_columns(table_name)

    for column in columns:
        if column["name"] in [
            "data_uri",
            "datacard_uri",
        ]:
            logger.info("Dropping {} column from {} table", column["name"], table_name)
            with op.batch_alter_table(table_name) as batch_op:
                batch_op.drop_column(column["name"])

    # data table cleanup
    table_name = RegistryTableNames.RUN.value
    columns = insp.get_columns(table_name)

    for column in columns:
        if column["name"] in ["runcard_uri"]:
            logger.info("Dropping {} column from {} table", column["name"], table_name)
            with op.batch_alter_table(table_name) as batch_op:
                batch_op.drop_column(column["name"])


def downgrade() -> None:
    table_name = RegistryTableNames.MODEL.value
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(sa.Column("trained_model_uri", sa.String(1024)))
        batch_op.add_column(sa.Column("modelcard_uri", sa.String(1024)))
        batch_op.add_column(sa.Column("model_metadata_uri", sa.String(1024)))
        batch_op.add_column(sa.Column("sample_data_uri", sa.String(1024)))

    table_name = RegistryTableNames.DATA.value
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(sa.Column("data_uri", sa.String(1024)))
        batch_op.add_column(sa.Column("datacard_uri", sa.String(1024)))
        
    table_name = RegistryTableNames.RUN.value
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(sa.Column("runcard_uri", sa.String(512)))
