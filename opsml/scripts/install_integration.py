import click
from opsml.extras.integration_installer import get_installer
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


@click.command()
@click.option("--integration", help="Integration to download packages for", required=True, type=str)
@click.option(
    "--install_type", help="Type of installer to use (poetry or pip)", default="pip", required=False, type=str
)
def install_extra_packages(integration: str, install_type: str):
    installer = get_installer(integration_type=integration, install_type=install_type)

    logger.info("Installing packages for %s and install type: %s", integration, install_type)
    installer.install()


if __name__ == "__main__":
    install_extra_packages()  # pylint: disable=no-value-for-parameter
