"""alter table

Revision ID: b82c6a7cfebd
Revises: fd32b1afafd5
Create Date: 2023-04-12 14:54:54.305163

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

from opsml_artifacts.registry.sql.sql_schema import (
    DataSchema,
    ModelSchema,
    PipelineSchema,
    ProjectSchema,
    RunSchema,
)

REGISTRY_TABLES = [RunSchema, ModelSchema, PipelineSchema, DataSchema, ProjectSchema]

# revision identifiers, used by Alembic.
revision = "b82c6a7cfebd"
down_revision = "fd32b1afafd5"
branch_labels = None
depends_on = None


def alter_column(table_name: str, old_column: str, new_column: str):
    try:
        op.alter_column(table_name, old_column, new_column_name=new_column)
    except Exception as exc:
        print(exc)
        pass


def upgrade() -> None:

    conn = op.get_bind()
    op.create_table
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    # rename exp if present:
    if "OPSML_EXPERIMENT_REGISTRY" in tables:

        op.rename_table("OPSML_EXPERIMENT_REGISTRY", "OPSML_RUN_REGISTRY")

    # try renaming columns before table creations
    alter_column(RunSchema.__tablename__, "data_card_uids", "datacard_uids")
    alter_column(RunSchema.__tablename__, "model_card_uids", "modelcard_uids")
    alter_column(RunSchema.__tablename__, "pipeline_card_uid", "pipelinecard_uid")

    for table in REGISTRY_TABLES:
        if table.__tablename__ not in tables:
            table.__table__.create(bind=conn, checkfirst=True)

    alter_column(ModelSchema.__tablename__, "model_card_uri", "modelcard_uri")
    alter_column(ModelSchema.__tablename__, "data_card_uid", "datacard_uid")

    alter_column(PipelineSchema.__tablename__, "data_card_uids", "datacard_uids")
    alter_column(PipelineSchema.__tablename__, "model_card_uids", "modelcard_uids")
    alter_column(PipelineSchema.__tablename__, "experiment_card_uids", "runcard_uids")
    # Update


def downgrade() -> None:
    pass
