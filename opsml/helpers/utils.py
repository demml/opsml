"""Suite of helper objects"""
import glob
import os
import re
import string
from pathlib import Path
from typing import Optional, Union

from . import exceptions

PUNCTUATION = string.punctuation.replace("_", "").replace("-", "")
REMOVE_CHARS = re.escape(PUNCTUATION)


def clean_string(name: Optional[str] = None) -> Optional[str]:
    if name is not None:
        _name = name.strip()
        _name = _name.lower()
        _name = re.sub("[" + REMOVE_CHARS + "]", "", _name)
        _name = _name.replace("_", "-")

        return _name
    return None


class TypeChecker:
    @staticmethod
    def check_metric_type(metric: Union[int, float]):
        if isinstance(metric, (int, float)):
            return metric
        raise ValueError("Metric is not of valid type (int, float)")

    @staticmethod
    def check_param_type(param: Union[int, float, str]):
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
            raise ValueError(f"No path found for file {name}. {error}") from error

        if file_path is not None:
            return file_path

        raise exceptions.MissingKwarg(
            f"""
            {name} file was not found in the current path: {path}.
            Check to make sure you specified the correct name.
            """
        )

    @staticmethod
    def find_dirpath(
        dir_name: str,
        path: str,
        anchor_file: str,
    ):
        """Finds the dir path of a given file.

        Args:
            dir_name (str): Name of directory
            path (str): Optional. Base path to search
            anchor_file (str): Name of anchor file in directory

        Returns:
            dirpath (str)
        """

        paths = glob.glob(f"{path}/**/{anchor_file}", recursive=True)

        if len(paths) <= 1:
            new_path: Union[list, str] = []
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

            new_path = "/".join(dirs[: dir_idx + 1])
            return new_path

        raise exceptions.MoreThanOnePath(
            f"""More than one path was found for the trip configuration file.
                Please check your project structure.
                Found paths: {paths}
            """
        )

    @staticmethod
    def find_source_dir(
        path: str,
        runner_file: str,
    ):
        """Finds the dir path of a given of the pipeline
        runner file.

        Args:
            path (str): Current directory
            runner_file (str): Name of pipeline runner file

        Returns:
            dirpath (str)
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


def all_subclasses(cls):
    """Gets all subclasses associated with parent class"""
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)],
    )
