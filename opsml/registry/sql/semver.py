from typing import List
import re
from enum import Enum


def sort_semvers(semvers: List[str]):
    """Sorts a list of semvers"""
    semvers.sort(key=lambda x: [int(y) for y in x.split(".")])
    semvers.reverse()


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
