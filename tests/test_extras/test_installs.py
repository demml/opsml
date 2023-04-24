from click.testing import CliRunner
from opsml.scripts.install_integration import install_extra_packages
from opsml.extras.types import IntegrationType, InstallType
from unittest.mock import patch, MagicMock
import pytest


@pytest.mark.parametrize(
    "integration",
    [
        IntegrationType.GCP.value,
        IntegrationType.KUBEFLOW.value,
        IntegrationType.VERTEX.value,
    ],
)
@pytest.mark.parametrize(
    "install_type",
    [
        InstallType.PIP.value,
        InstallType.POETRY.value,
    ],
)
def test_gcp_install(integration, install_type):

    with patch.multiple(
        "opsml.extras.installer_base.Installer",
        install=MagicMock(return_value=None),
    ):
        args = ["--integration", integration, "--install_type", install_type]

        runner = CliRunner()
        result = runner.invoke(install_extra_packages, args)
        assert result.exit_code == 0
