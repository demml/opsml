import re
from enum import Enum
from typing import List
import semver
from dataclasses import dataclass


@dataclass
class CardVersion:
    version: str

    def __post_init__(self):
        """Validates a user-supplied version"""
        if self.is_full_semver:
            self._validate_full_semver()
        else:
            self._validate_partial_semver()

    @property
    def valid_version(self) -> str:
        if self.is_full_semver:
            return str(semver.VersionInfo.parse(self.version).finalize_version())
        return self.version

    def _validate_full_semver(self):
        """Validates a full semver"""
        if not semver.VersionInfo.isvalid(self.version):
            raise ValueError("Version is not a valid Semver")

    @property
    def is_full_semver(self) -> bool:
        """Checks if a version is a full or partial semver
        Args:
            version:
                version to check
        Returns:
            bool: True if version is a full semver, False otherwise
        """
        if len(self.version.split(".")) < 3:
            return False
        return True

    def _validate_partial_semver(self) -> None:
        """Validates a partial semver"""
        version_splits = self.version.split(".")
        try:
            assert all([i.isdigit() for i in version_splits])
        except AssertionError:
            raise AssertionError(f"Version {self.version} is not a valid semver or partial semver")

    @staticmethod
    def finalize_partial_version(version: str) -> str:
        """Finalizes a partial semver version

        Args:
            version:
                version to finalize
        Returns:
            str: finalized version
        """
        version_splits = version.split(".")

        if len(version_splits) == 1:
            return f"{version}.0.0"
        elif len(version_splits) == 2:
            return f"{version}.0"

        return version


def sort_semvers(semvers: List[str]) -> List[str]:
    """Sorts a list of semvers"""
    sorted_versions = sorted(
        semvers, key=lambda x: [int(i) if i.isdigit() else i for i in x.replace("-", ".").split(".")]
    )
    sorted_versions.reverse()
    return sorted_versions


class SemVerSymbols(str, Enum):
    STAR = "*"
    CARET = "^"
    TILDE = "~"


class SemVerParser:
    """Base class for semver parsing"""

    @staticmethod
    def parse_version(version: str) -> str:
        raise NotImplementedError

    @staticmethod
    def validate(version: str) -> bool:
        raise NotImplementedError


class StarParser(SemVerParser):
    """Parses versions that contain * symbol"""

    @staticmethod
    def parse_version(version: str) -> str:
        version_ = version.split(SemVerSymbols.STAR)[0]
        return re.sub(".$", "", version_)

    @staticmethod
    def validate(version: str) -> bool:
        return SemVerSymbols.STAR in version


class CaretParser(SemVerParser):
    """Parses versions that contain ^ symbol"""

    @staticmethod
    def parse_version(version: str) -> str:
        return version.split(".")[0].replace(SemVerSymbols.CARET, "")

    @staticmethod
    def validate(version: str) -> bool:
        return SemVerSymbols.CARET in version


class TildeParser(SemVerParser):
    """Parses versions that contain ~ symbol"""

    @staticmethod
    def parse_version(version: str) -> str:
        return ".".join(version.split(".")[0:2]).replace(SemVerSymbols.TILDE, "")

    @staticmethod
    def validate(version: str) -> bool:
        return SemVerSymbols.TILDE in version


class NoParser(SemVerParser):
    """Does not parse version"""

    @staticmethod
    def parse_version(version: str) -> str:
        return version

    @staticmethod
    def validate(version: str) -> bool:
        return version not in list(SemVerSymbols)


def get_version_to_search(version: str) -> str:
    """Parses a current version based on SemVer characters.

    Args:
        version (str): ArtifactCard version

    Returns:
        Version (str) to search based on presence of SemVer characters
    """

    # gut check
    if sum(symbol in version for symbol in SemVerSymbols) > 1:
        raise ValueError("Only one SemVer character is allowed in the version string")

    parser = next(
        (parser for parser in SemVerParser.__subclasses__() if parser.validate(version=version)),
        NoParser,
    )
    return parser.parse_version(version=version)
