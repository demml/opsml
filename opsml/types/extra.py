# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from enum import Enum, unique
from typing import Optional

from pydantic import BaseModel, field_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import FileUtils

logger = ArtifactLogger.get_logger()


@unique
class UriNames(str, Enum):
    TRAINED_MODEL_URI = "trained_model_uri"
    SAMPLE_DATA_URI = "sample_data_uri"
    PREPROCESSOR_URI = "preprocessor_uri"
    MODELCARD_URI = "modelcard_uri"
    MODEL_METADATA_URI = "model_metadata_uri"
    ONNX_MODEL_URI = "onnx_model_uri"
    DATA_URI = "data_uri"
    DATACARD_URI = "datacard_uri"
    PROFILE_URI = "profile_uri"
    PROFILE_HTML_URI = "profile_html_uri"
    RUNCARD_URI = "runcard_uri"
    ARTIFACT_URIS = "artifact_uris"
    QUANTIZED_MODEL_URI = "quantized_model_uri"
    TOKENIZER_URI = "tokenizer_uri"
    FEATURE_EXTRACTOR_URI = "feature_extractor_uri"


@unique
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
    TOKENIZER = "tokenizer"
    TOKENIZER_NAME = "tokenizer_name"
    FEATURE_EXTRACTOR = "feature_extractor"
    FEATURE_EXTRACTOR_NAME = "feature_extractor_name"
    IMAGE = "image"
    TEXT = "text"
    VOWPAL_ARGS = "arguments"
    BASE_VERSION = "0.0.0"


@unique
class SaveName(str, Enum):
    CARD = "card"
    AUDIT = "audit"
    PIPLELINECARD = "pipelinecard"
    MODEL_METADATA = "model-metadata"
    TRAINED_MODEL = "trained-model"
    PREPROCESSOR = "preprocessor"
    ONNX_MODEL = "onnx-model"
    SAMPLE_MODEL_DATA = "sample-model-data"
    DATA_PROFILE = "data-profile"
    DATA = "data"
    PROFILE = "profile"
    ARTIFACTS = "artifacts"
    QUANTIZED_MODEL = "quantized-model"
    TOKENIZER = "tokenizer"
    FEATURE_EXTRACTOR = "feature_extractor"
    METADATA = "metadata"
    GRAPHS = "graphs"


@unique
class Suffix(str, Enum):
    ONNX = ".onnx"
    PARQUET = ".parquet"
    ZARR = ".zarr"
    JOBLIB = ".joblib"
    HTML = ".html"
    JSON = ".json"
    CKPT = ".ckpt"
    PT = ".pt"
    TEXT = ".txt"
    CATBOOST = ".cbm"
    JSONL = ".jsonl"
    NONE = ""
    DMATRIX = ".dmatrix"
    MODEL = ".model"


@unique
class ArtifactClass(str, Enum):
    DATA = "data"
    OTHER = "other"


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


class GraphStyle(str, Enum):
    LINE = "line"
    SCATTER = "scatter"

    @staticmethod
    def from_str(name: str) -> "GraphStyle":
        l_name = name.strip().lower()
        if l_name == "line":
            return GraphStyle.LINE
        if l_name == "scatter":
            return GraphStyle.SCATTER
        raise ValueError(f"GraphStyle {name} not found")
