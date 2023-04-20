# Helper module for checking if required dependencies are present
import subprocess
import sys
from typing import List

from opsml.extras.types import InstallType


class Installer:
    def __init__(self, install_type: str):
        """
        Helper class for installing extra dependencies
        Args:
            dependencies:
                List of dependencies to check
        """
        self.install_type = install_type

    @property
    def packages(self) -> List[str]:
        raise NotImplementedError

    def _install_pip(self) -> None:
        """Installs required packages via pip"""
        subprocess.check_call([sys.executable, "-m", "pip", "install", *self.packages])

    def _install_poetry(self) -> None:
        """Installs required packages into active poetry env"""
        subprocess.run(["poetry", "add", *self.packages], check=True)

    def install(self) -> None:
        if self.install_type == InstallType.POETRY:
            return self._install_poetry()
        return self._install_pip()

    @staticmethod
    def validate(integration_type: str) -> bool:
        raise NotImplementedError
