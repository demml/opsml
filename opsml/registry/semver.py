# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import re
from enum import Enum
from typing import Any, List, Optional

import semver
from pydantic import BaseModel, model_validator

from opsml.helpers.exceptions import VersionError
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class VersionType(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRE = "pre"
    BUILD = "build"
    PRE_BUILD = "pre_build"

    @staticmethod
    def from_str(name: str) -> "VersionType":
        l_name = name.strip().lower()
        if l_name == "major":
            return VersionType.MAJOR
        if l_name == "minor":
            return VersionType.MINOR
        if l_name == "patch":
            return VersionType.PATCH
        if l_name == "pre":
            return VersionType.PRE
        if l_name == "build":
            return VersionType.BUILD
        if l_name == "pre_build":
            return VersionType.PRE_BUILD
        raise NotImplementedError()


class CardVersion(BaseModel):
    version: str
    version_splits: List[str] = []
    is_full_semver: bool = False

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values: Any) -> Any:
        """Validates a user-supplied version"""
        version = values.get("version")
        splits = version.split(".")
        values["version_splits"] = splits

        if cls.check_full_semver(splits):
            values["is_full_semver"] = True
            cls._validate_full_semver(version)
        else:
            values["is_full_semver"] = False
            cls._validate_partial_semver(splits)

        return values

    @classmethod
    def check_full_semver(cls, version_splits: List[str]) -> bool:
        """Checks if a version is a full semver"""
        return len(version_splits) >= 3

    @classmethod
    def _validate_full_semver(cls, version: str) -> None:
        """Validates a full semver"""
        if not semver.VersionInfo.isvalid(version):
            raise ValueError("Version is not a valid Semver")

    @classmethod
    def _validate_partial_semver(cls, version_splits: List[str]) -> None:
        """Validates a partial semver"""
        try:
            assert all((i.isdigit() for i in version_splits))
        except AssertionError as exc:
            version = ".".join(version_splits)
            raise AssertionError(f"Version {version} is not a valid semver or partial semver") from exc

    def _get_version_split(self, split: int) -> str:
        """Splits a version into its major, minor, and patch components"""

        try:
            return self.version_splits[split]
        except IndexError as exc:
            raise IndexError(f"Version split {split} not found: {self.version}") from exc

    @property
    def has_major_minor(self) -> bool:
        """Checks if a version has a major and minor component"""
        return len(self.version_splits) >= 2

    @property
    def major(self) -> str:
        return self._get_version_split(0)

    @property
    def minor(self) -> str:
        return self._get_version_split(1)

    @property
    def patch(self) -> str:
        return self._get_version_split(2)

    @property
    def valid_version(self) -> str:
        if self.is_full_semver:
            return str(semver.VersionInfo.parse(self.version).finalize_version())
        return self.version

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
        if len(version_splits) == 2:
            return f"{version}.0"

        return version

    def get_version_to_search(self, version_type: VersionType) -> Optional[str]:
        """Gets a version to search for in the database

        Args:
            version_type:
                type of version to search for
        Returns:
            str: version to search for
        """

        if version_type == VersionType.PATCH:  # want to search major and minor if exists
            if self.has_major_minor:
                return f"{self.major}.{self.minor}"
            return str(self.major)

        if version_type == VersionType.MINOR:  # want to search major
            return str(self.major)

        if version_type in [VersionType.PRE, VersionType.BUILD, VersionType.PRE_BUILD]:
            return self.valid_version

        return None


class SemVerUtils:
    """Class for general semver-related functions"""

    @staticmethod
    def sort_semvers(versions: List[str]) -> List[str]:
        """Implements bubble sort for semvers

        Args:
            versions:
                list of versions to sort

        Returns:
            sorted list of versions with highest version first
        """

        n_ver = len(versions)

        for i in range(n_ver):
            already_sorted = True

            for j in range(n_ver - i - 1):
                j_version = semver.VersionInfo.parse(versions[j])
                j1_version = semver.VersionInfo.parse(versions[j + 1])

                # use semver comparison logic
                if j_version > j1_version:
                    # swap
                    versions[j], versions[j + 1] = versions[j + 1], versions[j]

                    already_sorted = False

            if already_sorted:
                break

        versions.reverse()
        return versions

    @staticmethod
    def is_release_candidate(version: str) -> bool:
        """Ignores pre-release versions"""
        ver = semver.VersionInfo.parse(version)
        return bool(ver.prerelease)

    @staticmethod
    def increment_version(
        version: str,
        version_type: VersionType,
        pre_tag: str,
        build_tag: str,
    ) -> str:
        """
        Increments a version based on version type

        Args:
            version:
                Current version
            version_type:
                Type of version increment.
            pre_tag:
                Pre-release tag
            build_tag:
                Build tag

        Raises:
            ValueError:
                unknown version_type

        Returns:
            New version
        """
        ver: semver.VersionInfo = semver.VersionInfo.parse(version)

        # Set major, minor, patch
        if version_type == VersionType.MAJOR:
            return str(ver.bump_major())
        if version_type == VersionType.MINOR:
            return str(ver.bump_minor())
        if version_type == VersionType.PATCH:
            return str(ver.bump_patch())

        # Set pre-release
        if version_type == VersionType.PRE:
            return str(ver.bump_prerelease(token=pre_tag))

        # Set build
        if version_type == VersionType.BUILD:
            return str(ver.bump_build(token=build_tag))

        if version_type == VersionType.PRE_BUILD:
            ver = ver.bump_prerelease(token=pre_tag)
            ver = ver.bump_build(token=build_tag)

            return str(ver)

        raise ValueError(f"Unknown version_type: {version_type}")

    @staticmethod
    def add_tags(
        version: str,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
    ) -> str:
        if pre_tag is not None:
            version = f"{version}-{pre_tag}"
        if build_tag is not None:
            version = f"{version}+{build_tag}"

        return version


class SemVerRegistryValidator:
    """Class for obtaining the correct registry version"""

    def __init__(
        self,
        name: str,
        version_type: VersionType,
        pre_tag: str,
        build_tag: str,
        version: Optional[CardVersion] = None,
    ) -> None:
        """Instantiate SemverValidator

        Args:
            name:
                name of the artifact
            version_type:
                type of version increment
            version:
                version to use
            pre_tag:
                pre-release tag
            build_tag:
                build tag

        Returns:
            None
        """
        self.version = version
        self._version_to_search = None
        self.final_version = None
        self.version_type = version_type
        self.name = name
        self.pre_tag = pre_tag
        self.build_tag = build_tag

    @property
    def version_to_search(self) -> Optional[str]:
        """Parses version and returns version to search for in the registry"""
        if self.version is not None:
            return self.version.get_version_to_search(version_type=self.version_type)
        return self._version_to_search

    def _set_version_from_existing(self, versions: List[str]) -> str:
        """Search existing versions to find the correct version to use

        Args:
            versions:
                list of existing versions

        Returns:
            str: version to use
        """
        version = versions[0]
        recent_ver = semver.VersionInfo.parse(version)
        # first need to check if increment is mmp
        if self.version_type in [VersionType.MAJOR, VersionType.MINOR, VersionType.PATCH]:
            # check if most recent version is a pre-release or build
            if recent_ver.prerelease is not None:
                version = str(recent_ver.finalize_version())
                try:
                    # if all versions are pre-release use finalized version
                    # if not, increment version
                    for ver in versions:
                        parsed_ver = semver.VersionInfo.parse(ver)
                        if parsed_ver.prerelease is None:
                            raise VersionError("Major, minor and patch version combination already exists")
                    return version
                except VersionError:
                    logger.info("Major, minor and patch version combination already exists")

        while version in versions:
            version = SemVerUtils.increment_version(
                version=version,
                version_type=self.version_type,
                pre_tag=self.pre_tag,
                build_tag=self.build_tag,
            )

        return version

    def set_version(self, versions: List[str]) -> str:
        """Sets the correct version to use for incrementing and adding the the registry

        Args:
            versions:
                list of existing versions

        Returns:
            str: version to use
        """
        if bool(versions):
            return self._set_version_from_existing(versions=versions)

        final_version = None
        if self.version is not None:
            final_version = CardVersion.finalize_partial_version(version=self.version.valid_version)

        version = final_version or "1.0.0"

        if self.version_type in [VersionType.PRE, VersionType.BUILD, VersionType.PRE_BUILD]:
            return SemVerUtils.increment_version(
                version=version,
                version_type=self.version_type,
                pre_tag=self.pre_tag,
                build_tag=self.build_tag,
            )

        return version


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
