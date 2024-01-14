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
from regex import E

from opsml.helpers.logging import ArtifactLogger
from opsml.data.splitter import DataSplitter
from opsml.data.interfaces.custom_data.image import ImageMetadata, ImageRecord

logger = ArtifactLogger.get_logger()


class ImageData(BaseModel):

    """Create an image dataset from a directory of images and a metadata file.
    Splits will be inferred from the child of the parent data_dir if it exists.

    Args:
        data_dir:
            Root directory for images.

            For example, you the image file is located at either:
             - `images/train/my_image.png`
             - `images/my_image.png`
            Then the data_dir should be `images/`

        metadata:
            Metadata file for images. Can be a jsonl file or an ImageMetadata object.
            If a jsonl file is provided, it is expected that each line is a valid ImageRecord
            and that the file is located in the data_dir.

    """

    data_dir: Union[str, Path]
    metadata: Union[str, ImageMetadata]

    def check_metadata(self) -> None:
        """Validates if metadata is a jsonl file and if each record is valid"""
        if isinstance(self.metadata, str):
            # check metadata file is valid
            assert "jsonl" in self.metadata, "metadata must be a jsonl file"

            # Validate metadata file (load each file in as record)
            try:
                with open(self.metadata, "r", encoding="utf-8") as file_:
                    for line in file_:
                        ImageRecord(**json.loads(line))

            except Exception as e:
                raise ValueError(f"Invalid metadata file: {e}")

    def convert_metadata(self) -> None:
        """Converts metadata to jsonl file if metadata is an ImageMetadata object"""

        if isinstance(self.metadata, ImageMetadata):
            logger.info("convert metadata to jsonl file")
            filepath = os.path.join(self.data_dir, "metadata.jsonl")

            self.metadata.write_to_file(filepath)
