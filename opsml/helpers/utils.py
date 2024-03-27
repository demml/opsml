"""Suite of helper objects"""

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import importlib.util
import os
import re
import string
import tempfile
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Set, Type, Union

from opsml.helpers import exceptions
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

PUNCTUATION = string.punctuation.replace("_", "").replace("-", "")
REMOVE_CHARS = re.escape(PUNCTUATION)
NAME_REPOSITORY_PATTERN = r"^[a-z0-9]+([-a-z0-9]+)*/[-a-z0-9]+$"


def experimental_feature(func: Callable[..., None]) -> Callable[..., None]:
    """Decorator for experimental features"""

    @wraps(func)
    def wrapper(self: Any, *args: List[Any], **kwargs: Dict[Any, Any]) -> None:
        class_name = self.__class__.__name__

        logger.warning("Class {} and it's features are experimental and may not work as intended", class_name)
        func(self, *args, **kwargs)

    return wrapper


def clean_string(value: Optional[str] = None) -> Optional[str]:
    """
    Cleans a given string. Cleaning makes the string lowercase, trims,
    whitespace, removes punctuation except for dashes and underscores, and
    replaces all underscores with dashes.

    Examples:
        clean_string("  TEST  "") == "test"
        clean_string("  !!_-TEST-_!!   ") == "--test--"

    Args:
        value: string to clean
    """
    if value is None:
        return None

    clean = value.strip().lower()
    clean = re.sub("[" + REMOVE_CHARS + "]", "", clean)
    return clean.replace("_", "-")


def validate_name_repository_pattern(name: str, repository: str) -> None:
    """
    Validates name and repository combination

    Args:
        name:
            Card name
        repository:
            repository associated with card

    """
    name_repository = f"{repository}/{name}"

    pattern_match = bool(re.match(NAME_REPOSITORY_PATTERN, name_repository))

    if not pattern_match:
        raise ValueError(
            f"Name and Repository failed to match the required pattern. Pattern: {NAME_REPOSITORY_PATTERN}"
        )

    if len(name_repository) > 53:
        raise ValueError("Name and Repository combination must be 53 characters or less")


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

    @staticmethod
    def replace_spaces(key: str) -> str:
        return key.replace(" ", "_")


class FileUtils:
    """Helper class for finding paths to artifacts"""

    @staticmethod
    @contextmanager
    def create_tmp_path(
        path: str,
    ) -> Generator[str, None, None]:
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield os.path.join(tmpdirname, os.path.basename(path))

    @staticmethod
    def find_dirpath(path: str, dir_name: str, anchor_file: str) -> Path:
        """Finds the directory path for a directory `dir_name` which contains a
        given anchor file.

        Note that anchor_file must be unique within the recursive directory tree
        rooted at `path`.

        Args:
            path:
                Base path to search
            dir_name:
                Name of directory
            anchor_file:
                Name of anchor file in directory

        Example:
            /test/child/grandchild/test.txt

            find_dirpath("child", "/test", "test.txt") == "/test/child"
            find_dirpath("grandchild", "/test", "test.txt") ==
            "/test/child/grandchild"

        Returns:
            dirpath

        Raises:
            FileNotFoundError: The anchor file does not exist in any directory
            MoreThanOnePathException: Multiple anchor_files exist in the `path` hierarchy

        """
        paths = list(Path(path).rglob(anchor_file))

        if len(paths) == 0:
            raise FileNotFoundError()

        if len(paths) > 1:
            raise exceptions.MoreThanOnePathException()

        for parent in paths[0].parents:
            if parent.is_dir() and parent.name == dir_name:
                return parent

        raise FileNotFoundError()

    @staticmethod
    def find_filepath(name: str, path: Optional[str] = None) -> Path:
        """Finds the file path of a given file.

        Args:
            name:
                Name of file
            path:
                Directory to search. Defaults to the current working directory.

        Returns:
            filepath

        Raises
        """
        if path is None:
            path = os.getcwd()

        paths = list(Path(path).rglob(name))

        if len(paths) == 0:
            raise FileNotFoundError(f"File {name} not found in {path}")

        if len(paths) > 1:
            raise exceptions.MoreThanOnePathException()

        return paths[0]


def all_subclasses(cls: Type[Any]) -> Set[Type[Any]]:
    """Gets all subclasses associated with parent class"""
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)],
    )


def check_package_exists(package_name: str) -> bool:
    """Checks if package exists

    Args:
        package_name:
            Name of package to check

    Returns:
        True if package exists, False otherwise
    """
    return importlib.util.find_spec(package_name) is not None


def try_import(packages: List[str], extras_expression: str, context: str) -> None:
    """Imports packages

    If the package cannot be imported, an custom error is logged.

    Args:
        packages:
            List of packages to test
        extras_expression:
            Expression for installing extras
        context:
            Context for error message
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


class OpsmlImportExceptions:
    @staticmethod
    def try_torchonnx_imports() -> None:
        """Attempts to import packages needed for onnx conversion of sklearn models"""
        try_import(
            ["onnx", "onnxruntime"],
            "opsml[torch_onnx]",
            "If you wish to convert your model to onnx",
        )

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

    @staticmethod
    def try_tensorflow_import() -> None:
        """Attempts to import packages needed for the server registry"""

        try_import(
            ["mypackage"],
            "opsml[server]",
            "If you wish to use TensorFlowModel",
        )


def get_class_name(object_: object) -> str:
    """Parses object to get the fully qualified class name.
    Used during type checking to avoid unnecessary imports.

    Args:
        object_:
            object to parse
    Returns:
        fully qualified class name
    """
    klass = object_.__class__
    module = klass.__module__
    if module == "builtins":
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + klass.__qualname__


def startup_import_error_message(err: Exception) -> None:
    """Helper function to print error message when server packages are not found."""

    from rich.console import Console

    console = Console()
    console.print(
        (
            "Server packages not found. If using Opsml as a client, "
            "make sure to set OPSML_TRACKING_URI with the http uri of your server. "
            "If you wish to use Opsml as a server, install the server packages by running:"
            "[bold green] poetry add opsml\[server] [/bold green]"  # pylint: disable=anomalous-backslash-in-string
        ),
        style="bold red",
    )
    raise SystemExit(err)
