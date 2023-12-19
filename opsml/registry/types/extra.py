# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import FileUtils

logger = ArtifactLogger.get_logger()


class CommonKwargs(str, Enum):
    IS_PIPELINE = "is_pipeline"
    MODEL_TYPE = "model_type"
    MODEL_CLASS = "model_class"
    MODEL_ARCH = "model_arch"
    PREPROCESSOR_NAME = "preprocessor_name"
    PREPROCESSOR = "preprocessor"
    TASK_TYPE = "task_type"
    MODEL = "model"
    UNDEFINED = "undefined"
    BACKEND = "backend"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SAMPLE_DATA = "sample_data"
    ONNX = "onnx"
    LOAD_TYPE = "load_type"
    DATA_TYPE = "data_type"


class Description(BaseModel):
    summary: Optional[str] = None
    sample_code: Optional[str] = None
    Notes: Optional[str] = None

    @field_validator("summary", mode="before")
    @classmethod
    def load_summary(cls, summary: Optional[str]) -> Optional[str]:
        if summary is None:
            return summary

        if ".md" in summary.lower():
            try:
                mkdwn_path = FileUtils.find_filepath(name=summary)
                with open(mkdwn_path, "r", encoding="utf-8") as file_:
                    summary = file_.read()

            except IndexError as idx_error:
                logger.info(f"Could not load markdown file {idx_error}")

        return summary
