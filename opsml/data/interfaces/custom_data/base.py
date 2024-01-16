# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import pyarrow as pa
from pydantic import BaseModel, model_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.types import CommonKwargs, Description, Suffix

logger = ArtifactLogger.get_logger()


def check_for_dirs(data_dir: Path) -> List[str]:
    """Checks if data_dir contains subdirectories and returns a list of subdirectories

    Args:
        data_dir:
            Path to data directory

    Returns:
        List of subdirectories
    """
    dirs = [x.stem for x in data_dir.iterdir() if x.is_dir()]
    return dirs


def get_metadata_filepath(data_dir: Path, split: Optional[str] = None) -> List[Path]:
    """Loads metadata file from data_dir or subdirectory of data_dir

    Args:
        data_dir:
            Path to data directory
        split:
            Optional split to use for the dataset. If not provided, all images in the data_dir will be used.

    Returns:
        `ImageMetadata`
    """

    if split is not None:
        search_path = data_dir / split
    else:
        search_path = data_dir

    paths = [p for p in search_path.rglob("*.jsonl") if p.name == "metadata.jsonl"]

    if paths:
        return paths

    raise ValueError(f"Could not find metadata.jsonl in {search_path} or subdirectories")


class FileRecord(BaseModel):
    """Base record to associate with file

    Args:
        filepath:
            Path to the file relative to root directory
        size:
            Size of the file. This is inferred automatically if filepath is provided.

    """

    filepath: Path
    size: int

    @model_validator(mode="before")
    @classmethod
    def check_args(cls, data_args: Dict[str, Any]) -> Dict[str, Any]:
        filepath: Optional[Union[str, Path]] = data_args.get("filepath")
        size: Optional[int] = data_args.get("size")

        if isinstance(filepath, str):
            filepath = Path(filepath)

        # if reloading record
        if all([filepath, size]):
            return data_args

        # Check image exists
        assert filepath, "Filepath is required"

        assert filepath.exists(), f"File {filepath} does not exist"
        data_args["size"] = filepath.stat().st_size

        return data_args

    def to_arrow(self, data_dir: Path, split_label: Optional[str] = None) -> Any:
        """Create pyarrow record"""
        raise NotImplementedError


def yield_chunks(list_: List[Any], size: int) -> Iterator[List[Any]]:
    """Yield successive n-sized chunks from list.

    Args:
        list_:
            list to chunk
        size:
            size of chunks

    """
    for _, i in enumerate(range(0, len(list_), size)):
        yield list_[i : i + size]


class Metadata(BaseModel):
    """Base class for metadata"""

    records: List[FileRecord]

    def write_to_file(self, filepath: Path) -> None:
        """Write image metadata to jsonl file

        Args:
            filepath:
                Filepath to write metadata jsonl. Filename of metadata path should be `metadata.jsonl`

        """
        assert filepath.name == "metadata.jsonl", "Filename must be metadata.jsonl"

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding="utf-8") as file_:
            for record in self.records:
                dumped_record = record.model_dump()
                dumped_record["filepath"] = dumped_record["filepath"].as_posix()
                json.dump(dumped_record, file_)
                file_.write("\n")

    @classmethod
    def load_from_file(cls, filepath: Path) -> Any:
        """Load image metadata from jsonl file

        Args:
            filepath:
                Filepath to load metadata jsonl. Filename of metadata path should be `metadata.jsonl`

        """
        raise NotImplementedError

    @cached_property
    def size(self) -> int:
        """Total size of all images in metadata"""
        return sum(record.size for record in self.records)


class Dataset(BaseModel):
    """Create an image dataset from a directory of images.
    User can also provide a split that indicates the subdirectory of images to use.
    It is expected that each split contains a metadata.jsonl built from the ImageMetadata class.
    ImageDataset was built to have parity with HuggingFace.

    Args:
        data_dir:
            Root directory for images.

            For example, you the image file is located at either:
             - `images/train/my_image.png`
             - `images/my_image.png`
            Then the data_dir should be `images/`
        shard_size:
            Size of shards to use for dataset. Default is 512MB.
        splits:
            Dictionary of splits to use for dataset. If no splits are provided, then the
            data_dir or subdirs will be used as the split. It is expected that each split contains a
            metadata.jsonl built from the ImageMetadata class. It is recommended to allow opsml
            to create the splits for you.
    """

    data_dir: Path
    shard_size: str = "512MB"
    splits: Dict[Optional[str], Metadata] = {}
    description: Description = Description()

    def split_data(self) -> None:
        """Creates data splits based on subdirectories of data_dir and supplied split value

        Returns:
            None
        """
        raise NotImplementedError

    def save_data(self, path: Path) -> None:
        """Saves data to data_dir

        Args:
            path:
                Path to save data

        """
        raise NotImplementedError

    def load_data(self, path: Path, **kwargs: Union[int, str]) -> None:
        """Saves data to data_dir

        Args:
            path:
                Path to save data

            kwargs:
                Keyword arguments to pass to the data loader

        """
        raise NotImplementedError

    @property
    def arrow_schema(self) -> pa.Schema:
        """Returns schema for ImageDataset records"""
        raise NotImplementedError

    @staticmethod
    def name() -> str:
        raise NotImplementedError

    @property
    def data_type(self) -> str:
        return CommonKwargs.UNDEFINED.value

    @property
    def data_suffix(self) -> str:
        return Suffix.NONE.value
