# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from isort import file

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.data.splitter import DataSplitter
from opsml.data.interfaces.custom_data.base import FileRecord

logger = ArtifactLogger.get_logger()


class BBox(BaseModel):
    """Bounding box for an image

    Args:
        bbox:
            List of coordinates for bounding box
        categories:
            List of categories for bounding box
    """

    bbox: List[List[float]]
    categories: List[Union[str, int, float]]


class ImageRecord(FileRecord):
    """Image record to associate with image file

    Args:
        filename:
            Full path to the file
        data_dir:
            Path to the directory containing the file
        caption:
            Optional caption for image
        categories:
            Optional list of categories for image
        objects:
            Optional `BBox` for the image
        split:
            Optional split for the image. It is expected that split is name of the subdirectory
            that contains the file (i.e., `images/train/my_image.png`)

            Example:
                If the image file is in `images/train/` then split should be `train`

    """

    caption: Optional[str] = None
    categories: Optional[List[Union[str, int, float]]] = None
    objects: Optional[BBox] = None


class ImageMetadata(BaseModel):
    """Create Image metadata from a list of ImageRecords

    Args:

        Images:
            List of ImageRecords
    """

    images: List[ImageRecord]

    def write_to_file(self, filename: Path) -> None:
        """Write image metadata to file

        Args:
            filename:
                Path to file to write metadata to
        """

        filename.parent.mkdir(parents=True, exist_ok=True)
        with filename.open("w", encoding="utf-8") as file_:
            for record in self.records:
                json.dump(record.model_dump(), file_)
                file_.write("\n")

    @cached_property
    def size(self) -> int:
        """Total size of all images in metadata"""
        return sum([record.size for record in self.images])
