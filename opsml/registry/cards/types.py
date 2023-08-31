# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from dataclasses import dataclass
from enum import Enum
import json
import os
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator, ValidationInfo


@dataclass
class ModelCardUris:
    modelcard_uri: Optional[str] = None
    trained_model_uri: Optional[str] = None
    onnx_model_uri: Optional[str] = None
    model_metadata_uri: Optional[str] = None
    sample_data_uri: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=("protect_",))


@dataclass
class DataCardUris:
    data_uri: Optional[str] = None
    datacard_uri: Optional[str] = None
    profile_uri: Optional[str] = None
    profile_html_uri: Optional[str] = None


class Metric(BaseModel):
    name: str
    value: Union[float, int]
    step: Optional[int] = None
    timestamp: Optional[int] = None


class Param(BaseModel):
    name: str
    value: Union[float, int, str]


class BBox(BaseModel):
    bbox: List[List[float]]
    categories: List[Union[str, int, float]]


class ImageRecord(BaseModel):
    file_name: str
    caption: Optional[str] = None
    categories: Optional[List[Union[str, int, float]]] = None
    objects: Optional[BBox] = None


class ImageMetadata(BaseModel):
    records: List[ImageRecord]


class ImageDataset(BaseModel):
    image_dir: str
    metadata: Union[str, ImageMetadata]

    @field_validator("image_dir", mode="before")
    def check_dir(cls, value):
        assert os.path.isdir(value), "image_dir must be a directory"

        return value

    @field_validator("metadata", mode="before")
    def check_metadata(cls, value, info: ValidationInfo):
        if isinstance(value, str):
            # check metadata file is valid
            assert "json" in value, "metadata must be a json file"

            # file should exist in image dir
            filepath = os.path.join(info.data.get("image_dir"), value)

            assert os.path.isfile(filepath), f"metadata file {value} does not exist in image_dir"

            with open(filepath, "r") as file_:
                metadata_json = json.load(file_)
                ImageMetadata(records=metadata_json)

        return value


METRICS = Dict[str, List[Metric]]
PARAMS = Dict[str, List[Param]]


@dataclass
class StoragePath:
    uri: str


@dataclass
class CardInfo:

    """
    Class that holds info related to an Artifact Card

    Args:
        name:
            Name of card
        team:
            Team name
        user_email:
            Email
        uid:
            Unique id of card
        version:
            Version of card
        tags:
            Tags associated with card
    """

    name: Optional[str] = None
    team: Optional[str] = None
    user_email: Optional[str] = None
    uid: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class CardType(str, Enum):
    DATACARD = "data"
    RUNCARD = "run"
    MODELCARD = "model"
    PIPELINECARD = "pipeline"
    PROJECTCARD = "project"


class PipelineCardArgs(str, Enum):
    DATA_UIDS = "datacard_uids"
    MODEL_UIDS = "modelcard_uids"
    RUN_UIDS = "runcard_uids"


class RunCardArgs(str, Enum):
    DATA_UID = "datacard_uid"
    MODEL_UIDS = "modelcard_uids"
    PIPELINE_UID = "pipelinecard_uid"


NON_PIPELINE_CARDS = [card.value for card in CardType if card.value not in ["pipeline", "project"]]
