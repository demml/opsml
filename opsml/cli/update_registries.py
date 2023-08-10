# License: MIT

import click

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.migration.migrate import run_alembic_migrations

logger = ArtifactLogger.get_logger(__name__)


@click.command()
def update_registries() -> str:
    """Updates OPSML registries with recent alembic revision"""

    return run_alembic_migrations()
