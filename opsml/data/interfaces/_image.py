# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from numpy import isin

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator
from sqlalchemy import MetaData

from opsml.helpers.logging import ArtifactLogger
from opsml.data.splitter import DataSplitter
from opsml.data.interfaces.custom_data.image import ImageMetadata, ImageRecord


logger = ArtifactLogger.get_logger()


def check_for_dirs(data_dir: Path) -> List[str]:
    """Checks if data_dir contains subdirectories and returns a list of subdirectories

    Args:
        data_dir:
            Path to data directory

    Returns:
        List of subdirectories
    """
    dirs = [x.as_posix() for x in data_dir.iterdir() if x.is_dir()]
    return dirs


def load_metadata_from_file(data_dir: Path, split: Optional[str]) -> ImageMetadata:
    """Loads metadata file from data_dir or subdirectory of data_dir

    Args:
        data_dir:
            Path to data directory
        split:
            Optional split to use for the dataset. If not provided, all images in the data_dir will be used.

    Returns:
        `ImageMetadata`
    """
    search_path = data_dir

    if split is not None:
        search_path = data_dir / split

    for p in search_path.rglob("*.jsonl"):
        if p.name == "metadata.jsonl":
            return ImageMetadata.from_file(p)

    raise ValueError(f"Could not find metadata.jsonl in {data_dir} or subdirectories")


class ImageData(BaseModel):

    """Create an image dataset from a directory of images.
    User can also provide a split that indicates the subdirectory of images to use.
    It is expected that each split contains a metadata.jsonl built from the ImageMetadata class.
    ImageData was built to have parity with HuggingFace.

    Args:
        data_dir:
            Root directory for images.

            For example, you the image file is located at either:
             - `images/train/my_image.png`
             - `images/my_image.png`
            Then the data_dir should be `images/`
        shard_size:
            Size of shards to use for dataset. Default is 512MB.
        batch_size:
            Batch size for dataset. Default is 1000.
        splits:
            Dictionary of splits to use for dataset. If no splits are provided, then the
            data_dir or subdirs will be used as the split. It is expected that each split contains a
            metadata.jsonl built from the ImageMetadata class. It is recommended to allow opsml
            to create the splits for you.
    """

    data_dir: Path
    shard_size: str = "512MB"
    batch_size: int = 1000
    splits: Dict[str, ImageMetadata] = {}

    def split_data(self) -> None:
        """Creates data splits based on subdirectories of data_dir and supplied split value

        Returns:
            `ImageSplitHolder`
        """
        if bool(self.splits):
            return

        splits = check_for_dirs(self.data_dir)

        if bool(splits):
            for split in splits:
                self.splits[split] = load_metadata_from_file(self.data_dir, split)
        else:
            self.splits["all"] = load_metadata_from_file(self.data_dir, None)
