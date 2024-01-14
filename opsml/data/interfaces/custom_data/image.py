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
from opsml.data.interfaces.custom_data.base import FileRecord, Metadata

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
        filepath:
            Full path to the file
        caption:
            Optional caption for image
        categories:
            Optional list of categories for image
        objects:
            Optional `BBox` for the image
        size:
            Size of the file. This is inferred automatically if filepath is provided.

    """

    caption: Optional[str] = None
    categories: Optional[List[Union[str, int, float]]] = None
    objects: Optional[BBox] = None


class ImageMetadata(Metadata):
    """Create Image metadata from a list of ImageRecords

    Args:

        records:
            List of ImageRecords
    """

    records: List[ImageRecord]
