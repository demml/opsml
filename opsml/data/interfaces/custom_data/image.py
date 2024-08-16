# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PIL import Image
from pydantic import BaseModel

from opsml.data.interfaces.custom_data.base import FileRecord, Metadata
from opsml.helpers.logging import ArtifactLogger

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

    def to_arrow(self, data_dir: Path, split_label: Optional[str] = None) -> Dict[str, Any]:
        """Saves data to arrow format

        Args:
            data_dir:
                Path to data directory
            split_label:
                Optional split label for data

        Returns:
            Dictionary of data to be saved to arrow
        """
        path = self.filepath.relative_to(data_dir)

        with Image.open(self.filepath) as img:
            stream_record = {
                "split_label": split_label,
                "path": path.as_posix(),
                "height": img.height,
                "width": img.width,
                "bytes": img.tobytes(),
                "mode": img.mode,
            }
        return stream_record


class ImageMetadata(Metadata):
    """Create Image metadata from a list of ImageRecords

    Args:

        records:
            List of ImageRecords
    """

    records: List[ImageRecord]

    @classmethod
    def load_from_file(cls, filepath: Path) -> "ImageMetadata":
        """Load metadata from a file

        Args:
            filepath:
                Path to metadata file
        """
        assert filepath.name == "metadata.jsonl", "Filename must be metadata.jsonl"
        with filepath.open("r", encoding="utf-8") as file_:
            records = []
            for line in file_:
                records.append(ImageRecord(**json.loads(line)))
            return cls(records=records)
