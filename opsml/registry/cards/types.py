# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, ConfigDict, field_validator
from opsml.helpers.logging import ArtifactLogger
from opsml.model.types import ApiDataSchemas, DataDict, ExtraOnnxArgs, OnnxModelDefinition

logger = ArtifactLogger.get_logger()


class Metric(BaseModel):
    name: str
    value: Union[float, int]
    step: Optional[int] = None
    timestamp: Optional[int] = None


class Param(BaseModel):
    name: str
    value: Union[float, int, str]


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


class Description(BaseModel):
    summary: Optional[str] = None
    intended_use: Optional[str] = None
    sample_code: Optional[str] = None
    Notes: Optional[str] = None


@dataclass
class ModelCardUris:
    """Uri holder for ModelCardMetadata

    Args:
        modelcard_uri:
            URI of modelcard
        trained_model_uri:
            URI where model is stored
        sample_data_uri:
            URI of trained model sample data
        model_metadata_uri:
            URI where model metadata is stored
    """

    modelcard_uri: Optional[str] = None
    trained_model_uri: Optional[str] = None
    onnx_model_uri: Optional[str] = None
    model_metadata_uri: Optional[str] = None
    sample_data_uri: Optional[str] = None

    model_config = ConfigDict(
        protected_namespaces=("protect_",),
        frozen=False,
    )


class ModelCardMetadata(BaseModel):
    """Create modelcard metadata

    Args:
        description:
            Description for your model
        onnx_model_data:
            Pydantic model containing onnx data schema
        onnx_model_def:
            Pydantic model containing OnnxModel definition
        model_type:
            Type of model
        data_schema:
            Optional dictionary of the data schema used in model training
        additional_onnx_args:
            Optional pydantic model containing Torch args for model conversion to onnx.
        runcard_uid:
            RunCard associated with the ModelCard
        pipelinecard_uid:
            Associated PipelineCard
        uris:
            ModelCardUris object containing all uris associated with ModelCard
    """

    description: Description = Description()
    onnx_model_data: Optional[DataDict] = None
    onnx_model_def: Optional[OnnxModelDefinition] = None
    sample_data_type: Optional[str] = None
    model_type: Optional[str] = None
    additional_onnx_args: Optional[ExtraOnnxArgs] = None
    data_schema: Optional[ApiDataSchemas] = None
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None
    uris: ModelCardUris = ModelCardUris()

    model_config = ConfigDict(protected_namespaces=("protect_",))


@dataclass
class DataCardUris:
    """Data uri holder for DataCardMetadata

    Args:
        data_uri:
            Location where converted data is stored
        datacard_uri:
            Location where DataCard is stored
        profile_uri:
            Location where profile is stored
        profile_html_uri:
            Location where profile html is stored
    """

    data_uri: Optional[str] = None
    datacard_uri: Optional[str] = None
    profile_uri: Optional[str] = None
    profile_html_uri: Optional[str] = None


class DataCardMetadata(BaseModel):

    """Create a DataCard metadata

    Args:
        description:
            Description for your data
        feature_map:
            Map of features in data (inferred when converting to pyarrow table)
        feature_descriptions:
            Dictionary of features and their descriptions
        additional_info:
            Dictionary of additional info to associate with data
            (i.e. if data is tokenized dataset, metadata could be {"vocab_size": 200})
        data_uri:
            Location where converted pyarrow table is stored
        runcard_uid:
            Id of RunCard that created the DataCard
        pipelinecard_uid:
            Associated PipelineCard
        uris:
            DataCardUris object containing all uris associated with DataCard
    """

    description: Description = Description()
    feature_map: Optional[Dict[str, Optional[Any]]] = None
    data_type: Optional[str] = None
    feature_descriptions: Dict[str, str] = {}
    additional_info: Dict[str, Union[float, int, str]] = {}
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None
    uris: DataCardUris = DataCardUris()

    @field_validator("feature_descriptions", mode="before")
    def lower_descriptions(cls, feature_descriptions):
        if not bool(feature_descriptions):
            return feature_descriptions

        feat_dict = {}
        for feature, description in feature_descriptions.items():
            feat_dict[feature.lower()] = description.lower()
            return feat_dict


NON_PIPELINE_CARDS = [card.value for card in CardType if card.value not in ["pipeline", "project"]]
