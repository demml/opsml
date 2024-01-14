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

logger = ArtifactLogger.get_logger()


class FileRecord(BaseModel):
    """Base record to associate with file

    Args:
        filepath:
            Path to the file
        size:
            Size of the file. This is inferred automatically if filepath is provided.

    """

    filepath: str
    size: int

    @model_validator(mode="before")
    @classmethod
    def check_args(cls, data_args: Dict[str, Any]) -> Dict[str, Any]:
        filepath: Optional[str] = data_args.get("filepath")
        size: Optional[int] = data_args.get("size")

        # if reloading record
        if all([filepath, size]):
            return data_args

        # Check image exists
        assert filepath, "Filepath is required"

        assert filepath.exists(), f"Image file {filepath} does not exist"
        data_args["size"] = filepath.stat().st_size

        return data_args
