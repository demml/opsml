# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from enum import Enum, unique
from typing import Any, Dict, List, Optional

import bcrypt
from pydantic import BaseModel, field_validator, model_validator

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
    DRIFT_PROFILE_URI = "drift_profile_uri"
    RUNCARD_URI = "runcard_uri"
    ARTIFACT_URIS = "artifact_uris"
    QUANTIZED_MODEL_URI = "quantized_model_uri"
    TOKENIZER_URI = "tokenizer_uri"
    FEATURE_EXTRACTOR_URI = "feature_extractor_uri"
    ONNX_CONFIG_URI = "onnx_config_uri"


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
    SAMPLE_DATA_INTERFACE_TYPE = "sample_data_interface_type"


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
    ONNX_CONFIG = "onnx-config"
    DATASET = "dataset"
    DRIFT_PROFILE = "drift-profile"


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


class PresignableTypes(str, Enum):
    JPEG = ".jpeg"
    JPG = ".jpg"
    PNG = ".png"
    PDF = ".pdf"
    MD = ".md"
    TEXT = ".txt"
    CSV = ".csv"
    JSON = ".json"
    TIFF = ".tiff"
    GIF = ".gif"
    MP4 = ".mp4"
    PY = ".py"
    YML = ".yml"
    YAML = ".yaml"


class UserRepositories(BaseModel):
    data: List[str] = []
    models: List[str] = []
    runs: List[str] = []


class UserScope(BaseModel):
    """Base user scope model. Default is read and write.
    A user will be able to read from any repository, but only write to
    repositories that they create. If a user needs access to additional
    repositories, they will need to be granted access by an admin by updating
    their scope object.
    """

    read: bool = True
    write: bool = True
    delete: bool = False
    admin: bool = False
    repositories: UserRepositories = UserRepositories()

    @property
    def is_admin(self) -> bool:
        return self.admin


class User(BaseModel):
    username: str
    password: Optional[str] = None
    security_question: Optional[str] = None
    security_answer: Optional[str] = None
    hashed_password: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    scopes: UserScope = UserScope()
    watchlist: UserRepositories = UserRepositories()
    updated_username: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def check_password(cls, user_args: Dict[str, Any]) -> Dict[str, Any]:
        password = user_args.get("password")
        hashed_password = user_args.get("hashed_password")

        # check if password or hashed_password is provided
        if not password and not hashed_password:
            raise ValueError("Password or hashed_password must be provided")

        # use already hashed password. no need to hash
        if hashed_password:
            return user_args

        # hash password if not hashed (for user creation)
        if password and not hashed_password:
            # hash password
            pass_bytes = password.encode("utf-8")
            hashed = bcrypt.hashpw(pass_bytes, bcrypt.gensalt())

            user_args["hashed_password"] = hashed

        return user_args


class Message(BaseModel):
    uid: str
    registry: str
    message_id: Optional[int] = None
    user: str
    votes: int = 0
    content: str
    parent_id: Optional[int] = None
    created_at: Optional[float] = None
