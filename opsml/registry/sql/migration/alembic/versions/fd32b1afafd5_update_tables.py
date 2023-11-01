"""update tables

Revision ID: fd32b1afafd5
Revises: 
Create Date: 2023-04-11 23:07:56.160420

"""
from alembic import op

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()
# revision identifiers, used by Alembic.
revision = "fd32b1afafd5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    logger.info(f"Alembic initial revision: {revision}")
    pass


def downgrade() -> None:
    pass
