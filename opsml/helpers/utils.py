"""Suite of helper objects"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import glob
import importlib
import os
import re
import string
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from opsml.helpers import exceptions
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

PUNCTUATION = string.punctuation.replace("_", "").replace("-", "")
REMOVE_CHARS = re.escape(PUNCTUATION)
NAME_TEAM_PATTERN = r"^[a-z0-9]+([-a-z0-9]+)*:[-a-z0-9]+$"


def experimental_feature(func: Callable[..., None]) -> Callable[..., None]:
    """Decorator for experimental features"""

    @wraps(func)
    def wrapper(self: Any, *args: List[Any], **kwargs: Dict[Any, Any]) -> None:
        class_name = self.__class__.__name__

        logger.warning("Class {} and it's features are experimental and may not work as intended", class_name)
        func(self, *args, **kwargs)

    return wrapper


def clean_string(name: Optional[str] = None) -> Optional[str]:
    """
    Cleans a given string

    Args:
        name:
            String to clean

    """
    if name is not None:
        _name = name.strip()
        _name = _name.lower()
        _name = re.sub("[" + REMOVE_CHARS + "]", "", _name)
        _name = _name.replace("_", "-")

        return _name
    return None


def validate_name_team_pattern(name: str, team: str) -> None:
    """
    Validates name and team combination

    Args:
        name:
            Card name
        team:
            Team associated with card

    """
    name_team = f"{name}:{team}"
    pattern_match = bool(re.match(NAME_TEAM_PATTERN, name_team))

    if not pattern_match:
        raise ValueError(f"Name and team failed to match the required pattern. Pattern: {NAME_TEAM_PATTERN}")

    if len(name_team) > 53:
        raise ValueError("Name and team combination must be 53 characters or less")


class TypeChecker:
    @staticmethod
    def check_metric_type(metric: Union[int, float]) -> Union[int, float]:
        if isinstance(metric, (int, float)):
            return metric
        raise ValueError("Metric is not of valid type (int, float)")

    @staticmethod
    def check_param_type(param: Union[int, float, str]) -> Union[int, float, str]:
        if isinstance(param, (int, float, str)):
            return param
        raise ValueError("Param is not of valid type (int, float, str)")


class FindPath:
    """Helper class for finding paths to artifacts"""

    @staticmethod
    def find_filepath(name: str, path: Optional[str] = None) -> Path:
        """Finds the file path of a given file.

        Args:
            name:
                Name of file
            path:
                Optional. Base path to search

        Returns:
            filepath
        """
        if path is None:
            path = os.getcwd()

        paths = list(Path(path).rglob(name))

        try:
            file_path = paths[0]
        except IndexError as error:
            raise IndexError(f"No path found for file {name}. {error}") from error

        if file_path is not None:
            return file_path

        raise exceptions.MissingKwarg(
            f"""
            {name} file was not found in the current path: {path}.
            Check to make sure you specified the correct name.
            """
        )

    @staticmethod
    def find_dirpath(dir_name: str, path: str, anchor_file: str) -> str:
        """Finds the dir path of a given file.

        Args:
            dir_name:
                Name of directory
            path:
                Base path to search
            anchor_file:
                Name of anchor file in directory

        Returns:
            dirpath
        """

        paths = glob.glob(f"{path}/**/{anchor_file}", recursive=True)

        if len(paths) <= 1:
            dirs = paths[0].split("/")[:-1]

            try:
                dir_idx = dirs.index(dir_name)
            except ValueError as error:
                raise exceptions.DirNotFound(
                    f"""Directory {dir_name} was not found.
                     Please check the name of your top-level directory.
                     Error: {error}
                     """
                )
            return "/".join(dirs[: dir_idx + 1])

        raise exceptions.MoreThanOnePath(
            f"""More than one path was found for the trip configuration file.
                Please check your project structure.
                Found paths: {paths}
            """
        )

    @staticmethod
    def find_source_dir(path: str, runner_file: str) -> Tuple[str, str]:
        """Finds the dir path of a given of the pipeline
        runner file.

        Args:
            path (str): Current directory
            runner_file (str): Name of pipeline runner file

        Returns:
            tuple(dir, name)
        """
        paths = glob.glob(f"{path}/**/{runner_file}", recursive=True)
        if len(paths) <= 1:
            source_path = "/".join(paths[0].split("/")[:-1])
            source_dir = paths[0].split("/")[:-1][-1]
            return source_dir, source_path

        raise exceptions.MoreThanOnePath(
            f"""More than one path was found for the trip configuration file.
                Please check your project structure.
                Found paths: {paths}
            """
        )


def all_subclasses(cls: Any) -> Set[Any]:
    """Gets all subclasses associated with parent class"""
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)],
    )


def try_import(packages: List[str], extras_expression: str, context: str) -> bool:
    """Test if packages can be imported

    Args:
        packages:
            List of packages to test
        extras_expression:
            Expression for installing extras
        context:
            Context for error message

    Returns:
        True if all packages can be imported, False otherwise
    """
    for package in packages:
        try:
            importlib.import_module(package)
        except ModuleNotFoundError as error:
            package_str = ", ".join(packages)
            logger.error(
                """Failed to import packages {}. Please install via opsml extras ({})
                {}""",
                package_str,
                extras_expression,
                context,
            )
            raise error
    return True


class OpsmlImportExceptions:
    @staticmethod
    def try_skl2onnx_imports() -> None:
        """Attempts to import packages needed for onnx conversion of sklearn models"""
        try_import(
            ["skl2onnx", "onnxmltools"],
            "opsml[sklearn_onnx]",
            "If you wish to convert your model to onnx",
        )

    @staticmethod
    def try_tf2onnx_imports() -> None:
        """Attempts to import packages needed for onnx conversion of tensorflow models"""

        try_import(
            ["tf2onnx"],
            "opsml[tf_onnx]",
            "If you wish to convert your model to onnx",
        )

    @staticmethod
    def try_sql_import() -> None:
        """Attempts to import packages needed for the server registry"""

        try_import(
            ["sqlalchemy", "alembic"],
            "opsml[server]",
            "If you wish to use the server registry",
        )
