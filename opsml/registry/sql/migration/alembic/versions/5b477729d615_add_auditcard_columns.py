"""add auditcard columns

Revision ID: 5b477729d615
Revises: fd32b1afafd5
Create Date: 2023-10-24 14:10:02.062476

"""
import sqlalchemy as sa
from alembic import op

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.sql_schema import RegistryTableNames

logger = ArtifactLogger.get_logger()


# revision identifiers, used by Alembic.
revision = "5b477729d615"
down_revision = "fd32b1afafd5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    logger.info(f"Alembic revision: add auditcard_uid and uris cols - {revision}")

    bind = op.get_context().bind
    insp = sa.inspect(bind)
    columns = insp.get_columns(RegistryTableNames.DATA.value)

    for table_name in [
        RegistryTableNames.DATA.value,
        RegistryTableNames.MODEL.value,
        RegistryTableNames.RUN.value,
    ]:
        columns = insp.get_columns(table_name)
        if not "auditcard_uid" in [column["name"] for column in columns]:
            logger.info(f"Migration Adding auditcard column to {table_name} table")
            with op.batch_alter_table(table_name) as batch_op:
                batch_op.add_column(sa.Column("auditcard_uid", sa.String(2048)))

                if table_name == RegistryTableNames.DATA.value:
                    if not "uris" in [column["name"] for column in columns]:
                        logger.info("Migration Adding uris column to data table")
                        batch_op.add_column(sa.Column("uris", sa.JSON))


def downgrade() -> None:
    logger.info("Dropping uris column from data table")
    for table_name in [
        RegistryTableNames.DATA.value,
        RegistryTableNames.MODEL.value,
        RegistryTableNames.RUN.value,
    ]:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column("auditcard_uid")

            if table_name == RegistryTableNames.DATA.value:
                batch_op.drop_column("uris")
