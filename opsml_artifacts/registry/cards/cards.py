from functools import cached_property
from typing import Any, Dict, List, Optional, TypeVar, Union, cast

import numpy as np
import pandas as pd
from pyarrow import Table
from pydantic import BaseModel, root_validator, validator
from pyshipt_logging import ShiptLogging

from opsml_artifacts.drift.data_drift import DriftReport
from opsml_artifacts.registry.cards.artifact_storage import (
    load_record_artifact_from_storage,
    save_record_artifact_to_storage,
)
from opsml_artifacts.registry.cards.storage_system import StorageClientObj
from opsml_artifacts.registry.cards.types import SaveInfo, StoragePath
from opsml_artifacts.registry.data.formatter import ArrowTable, DataFormatter
from opsml_artifacts.registry.data.splitter import DataHolder, DataSplitter
from opsml_artifacts.registry.model.creator import OnnxModelCreator
from opsml_artifacts.registry.model.predictor import OnnxModelPredictor
from opsml_artifacts.registry.model.types import (
    DataDict,
    Feature,
    ModelDefinition,
    OnnxModelReturn,
    TorchOnnxArgs,
)
from opsml_artifacts.registry.sql.records import (
    DataRegistryRecord,
    ExperimentRegistryRecord,
    ModelRegistryRecord,
    PipelineRegistryRecord,
)

logger = ShiptLogging.get_logger(__name__)

CardObj = TypeVar("CardObj", bound="ArtifactCard")


class ArtifactCard(BaseModel):
    """Base pydantic class for artifacts"""

    name: str
    team: str
    user_email: str
    version: Optional[int] = None
    uid: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = False
        smart_union = True

    def _set_additional_attr(
        self,
        uid: str,
        version: int,
        storage_client: StorageClientObj,
    ):
        setattr(self, "uid", uid)
        setattr(self, "version", version)
        setattr(self, "storage_client", storage_client)

    def create_registry_record(
        self,
        uid: str,
        version: int,
        registry_name: str,
        storage_client: StorageClientObj,
    ) -> Any:
        """Creates a registry record from self attributes

        Args:
            registry_name (str): Name of registry
            uid (str): Unique id associated with artifact
            version (int): Version for artifact
        """


class DataCard(ArtifactCard):
    """Create a DataCard from your data.

    Args:
        data (np.ndarray, pd.DataFrame, pa.Table): Data to use for
        data card.
        name (str): What to name the data
        team (str): Team that this data is associated with
        user_email (str): Email to associate with data card
        drift_report (dictioary of DriftReports): Optional drift report generated by Drifter class
        dependent_vars (List[str]): Optional list of dependent variables in data
        feature_descriptions (Dictionary): Optional dictionary of feature names and their descriptions
        data_splits (List of dictionaries): Optional list containing split logic. Defaults
        to None. Logic for data splits can be defined in the following three ways:

        You can specify as many splits as you'd like

        (1) Split based on column value (works for pd.DataFrame)
            splits = [
                {"label": "train", "column": "DF_COL", "column_value": 0}, -> "val" can also be a string
                {"label": "test",  "column": "DF_COL", "column_value": 1},
                {"label": "eval",  "column": "DF_COL", "column_value": 2},
                ]

        (2) Index slicing by start and stop (works for np.ndarray, pyarrow.Table, and pd.DataFrame)
            splits = [
                {"label": "train", "start": 0, "stop": 10},
                {"label": "test", "start": 11, "stop": 15},
                ]

        (3) Index slicing by list (works for np.ndarray, pyarrow.Table, and pd.DataFrame)
            splits = [
                {"label": "train", "indices": [1,2,3,4]},
                {"label": "test", "indices": [5,6,7,8]},
                ]

        The following are non-required args and are set after registering a DataCard

        data_uri (str): GCS location where converted pyarrow table is stored
        drift_uri (str): GCS location where drift report is stored
        version (int): DataCard version
        feature_map (dictionary): Map of features in data (inferred when converting to pyrarrow table)
        data_type (str): Data type inferred from supplied data
        uid (str): Unique id assigned to the DataCard
        dependent_vars (list): List of dependent variables. Can be string or index if using numpy
        feature_descriptions (dict): Dictionary of features and their descriptions
        additional_info (dict): Dictionary of additional info to associate with data
        (i.e. if data is tokenized dataset, metadata could be {"vocab_size": 200})


    Returns:
        DataCard

    """

    data: Optional[Union[np.ndarray, pd.DataFrame, Table]]
    drift_report: Optional[Dict[str, DriftReport]]
    data_splits: Optional[List[Dict[str, Any]]]
    data_uri: Optional[str]
    drift_uri: Optional[str]
    feature_map: Optional[Dict[str, Union[str, None]]]
    data_type: Optional[str]
    dependent_vars: Optional[List[Union[int, str]]]
    feature_descriptions: Optional[Dict[str, str]]
    additional_info: Optional[Dict[str, Union[float, int, str]]]
    storage_client: Optional[StorageClientObj]

    @property
    def has_data_splits(self):
        return bool(self.data_splits)

    @validator("data_uri", pre=True, always=True)
    def check_data(cls, data_uri, values):  # pylint: disable=no-self-argument

        if data_uri is None and values["data"] is None:
            raise ValueError("Data must be supplied when no data_uri is present")

        return data_uri

    @validator("data_splits", pre=True, always=True)
    def check_splits(cls, splits):  # pylint: disable=no-self-argument
        if splits is None:
            return []

        for split in splits:
            indices = split.get("indices")
            if indices is not None and isinstance(indices, np.ndarray):
                split["indices"] = indices.tolist()

        return splits

    @validator("feature_descriptions", pre=True, always=True)
    def lower_descriptions(cls, feature_descriptions):  # pylint: disable=no-self-argument

        if feature_descriptions is None:
            return feature_descriptions

        feat_dict = {}
        for feature, description in feature_descriptions.items():
            feat_dict[feature.lower()] = description.lower()

        return feat_dict

    @validator("additional_info", pre=True, always=True)
    def check_info(cls, value):  # pylint: disable=no-self-argument
        return value or {}

    def overwrite_converted_data_attributes(self, converted_data: ArrowTable):
        setattr(self, "data_uri", converted_data.storage_uri)
        setattr(self, "feature_map", converted_data.feature_map)
        setattr(self, "data_type", converted_data.table_type)

    def split_data(self) -> Optional[DataHolder]:

        """Loops through data splits and splits data either by indexing or
        column values

        Returns
            Class containing data splits
        """

        if not self.has_data_splits:
            return None

        data_splits: DataHolder = self._parse_data_splits()
        return data_splits

    def _parse_data_splits(self) -> DataHolder:

        data_holder = DataHolder()
        self.data_splits = cast(List[Dict[str, Any]], self.data_splits)
        for split in self.data_splits:
            label, data = DataSplitter(split_attributes=split).split(data=self.data)
            setattr(data_holder, label, data)

        return data_holder

    def _convert_and_save_data(self, blob_path: str, version: int) -> None:

        """Converts data into a pyarrow table or numpy array and saves to gcs.

        Args:
            Data_registry (str): Name of data registry. This attribute is used when saving
            data in gcs.
        """

        converted_data: ArrowTable = DataFormatter.convert_data_to_arrow(data=self.data)
        converted_data.feature_map = DataFormatter.create_table_schema(converted_data.table)
        save_info = SaveInfo(
            blob_path=blob_path,
            name=self.name,
            version=version,
            team=self.team,
        )
        storage_path = save_record_artifact_to_storage(
            artifact=converted_data.table,
            save_info=save_info,
            storage_client=cast(StorageClientObj, self.storage_client),
        )
        converted_data.storage_uri = storage_path.uri

        # manually overwrite
        self.overwrite_converted_data_attributes(converted_data=converted_data)

    def _save_drift(self, blob_path: str, version: int) -> None:

        """Saves drift report to to backend storage"""

        if bool(self.drift_report):

            save_info = SaveInfo(
                blob_path=blob_path,
                name="drift_report",
                version=version,
                team=self.team,
            )

            storage_path = save_record_artifact_to_storage(
                artifact=self.drift_report,
                save_info=save_info,
                storage_client=cast(StorageClientObj, self.storage_client),
            )
            setattr(self, "drift_uri", storage_path.uri)

    def load_data(self):
        """Loads data"""

        if not bool(self.data):
            data = load_record_artifact_from_storage(
                storage_uri=self.data_uri,
                artifact_type=self.data_type,
                storage_client=self.storage_client,
            )

            setattr(self, "data", data)
        else:
            logger.info("Data has already been loaded")

    def create_registry_record(
        self,
        uid: str,
        version: int,
        registry_name: str,
        storage_client: StorageClientObj,
    ) -> DataRegistryRecord:

        """Creates required metadata for registering the current data card.
        Implemented with a DataRegistry object.

        Args:
            Data_registry (str): Name of data registry. This attribute is used when saving
            data in gcs.

        Returns:
            Regsitry metadata

        """
        self._set_additional_attr(uid=uid, version=version, storage_client=storage_client)
        self._convert_and_save_data(blob_path=registry_name, version=version)
        self._save_drift(blob_path=registry_name, version=version)

        return DataRegistryRecord(**self.__dict__)

    def add_info(self, info: Dict[str, Union[float, int, str]]):
        """Adds metadata to the existing DataCard metadatda dictionary

        Args:
            Metadata (dictionary): Dictionary containing name (str) and value (float, int, str) pairs
        to add to the current metadata set
        """

        curr_info = cast(Dict[str, Union[int, float, str]], self.additional_info)
        self.additional_info = {**info, **curr_info}


class ModelCard(ArtifactCard):
    """Create a ModelCard from your trained machine learning model.
    This Card is used in conjunction with the ModelCardCreator class.

    Args:
        name (str): Name for the model specific to your current project
        team (str): Team that this model is associated with
        user_email (str): Email to associate with card
        trained_model (any): Trained model. Can be of type sklearn, xgboost,
        ightgbm or tensorflow
        sample_input_data (pandas dataframe, numpy array, or dictionary of numpy arrays):
        Sample of data model was trained on
        uid (str): Unique id (assigned if card has been registered)
        version (int): Current version (assigned if card has been registered)
        data_card_uid (str): Uid of the DataCard associated with training the model
        onnx_model_data (DataDict): Pydantic model containing onnx data schema
        onnx_model_def (ModelDefinition): Pydantic model containing OnnxModel definition
        model_uri (str): GCS uri where model is stored
        model_type (str): Type of model
        data_schema (Dictionary): Optional dictionary of the data schema used in model training
        additional_onnx_args (TorchOnnxArgs): Optional pydantic model containing optional
        Torch args for model conversion.
        Can be expanded at a later date to handle other model type args.
    """

    trained_model: Optional[Any]
    sample_input_data: Optional[Union[pd.DataFrame, np.ndarray, Dict[str, np.ndarray]]]
    data_card_uid: Optional[str]
    onnx_model_data: Optional[DataDict]
    onnx_model_def: Optional[ModelDefinition]
    model_card_uri: Optional[str]
    trained_model_uri: Optional[str]
    sample_data_uri: Optional[str]
    sample_data_type: Optional[str]
    model_type: Optional[str]
    additional_onnx_args: TorchOnnxArgs = TorchOnnxArgs()
    data_schema: Optional[Dict[str, Feature]]
    storage_client: Optional[StorageClientObj]

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @root_validator(pre=True)
    def check_args(cls, values: Dict[str, Any]):  # pylint: disable=no-self-argument
        """Converts trained model to modelcard"""

        if all([values.get("uid"), values.get("version")]):
            return values

        if not cls._required_args_present(values=values):
            raise ValueError(
                """trained_model and sample_input_data are required for instantiating a ModelCard""",
            )

        return values

    @classmethod
    def _required_args_present(cls, values: Dict[str, Any]) -> bool:
        return all(
            values.get(var_) is not None
            for var_ in [
                "trained_model",
                "sample_input_data",
            ]
        )

    def load_trained_model(self):
        sample_data = load_record_artifact_from_storage(
            storage_uri=self.sample_data_uri,
            artifact_type=self.sample_data_type,
            storage_client=cast(StorageClientObj, self.storage_client),
        )

        trained_model = load_record_artifact_from_storage(
            storage_uri=self.trained_model_uri,
            artifact_type=self.model_type,
            storage_client=cast(StorageClientObj, self.storage_client),
        )

        setattr(self, "sample_input_data", sample_data)
        setattr(self, "trained_model", trained_model)

    def _save_model(self, blob_path: str, version: int) -> StoragePath:

        save_info = SaveInfo(
            blob_path=blob_path,
            name=f"{self.name}-trained-model",
            version=version,
            team=self.team,
        )
        return save_record_artifact_to_storage(
            artifact=self.trained_model,
            save_info=save_info,
            artifact_type=self.model_type,
            storage_client=cast(StorageClientObj, self.storage_client),
        )

    def save_modelcard(self, blob_path: str, version: int):

        save_info = SaveInfo(
            blob_path=blob_path,
            name=self.name,
            version=version,
            team=self.team,
        )
        modelcard_storage_path = save_record_artifact_to_storage(
            artifact=self.dict(exclude={"sample_input_data", "trained_model"}),
            save_info=save_info,
            storage_client=cast(StorageClientObj, self.storage_client),
        )

        trained_model_storage_path = self._save_model(blob_path=blob_path, version=version)

        # convert and store sample data
        converted_data: ArrowTable = DataFormatter.convert_data_to_arrow(data=self.sample_input_data)
        save_info.name = f"{self.name}-sample-data"
        sample_data_storage_path = save_record_artifact_to_storage(
            artifact=converted_data.table,
            save_info=save_info,
            storage_client=cast(StorageClientObj, self.storage_client),
        )

        setattr(self, "model_card_uri", modelcard_storage_path.uri)
        setattr(self, "trained_model_uri", trained_model_storage_path.uri)
        setattr(self, "sample_data_uri", sample_data_storage_path.uri)
        setattr(self, "sample_data_type", converted_data.table_type)

    def create_registry_record(
        self,
        uid: str,
        version: int,
        registry_name: str,
        storage_client: StorageClientObj,
    ) -> ModelRegistryRecord:
        """Creates a registry record from the current ModelCard

        registry_name (str): ModelCard Registry table making request
        uid (str): Unique id of ModelCard

        """

        if not bool(self.onnx_model_def):
            self._create_and_set_onnx_attr()

        self._set_additional_attr(uid=uid, version=version, storage_client=storage_client)
        self.save_modelcard(blob_path=registry_name, version=version)
        return ModelRegistryRecord(**self.__dict__)

    def _set_version_for_predictor(self) -> int:
        if self.version is None:
            logger.warning(
                """ModelCard has no version (not registered).
                Defaulting to 1 (for testing only)
            """
            )
            version = 1
        else:
            version = self.version

        return version

    def _set_onnx_attributes(self, onnx_model: OnnxModelReturn) -> None:

        setattr(
            self,
            "onnx_model_data",
            DataDict(
                data_type=onnx_model.data_type,
                input_features=onnx_model.onnx_input_features,
                output_features=onnx_model.onnx_output_features,
            ),
        )

        setattr(self, "onnx_model_def", onnx_model.model_definition)
        setattr(self, "data_schema", onnx_model.data_schema)
        setattr(self, "model_type", onnx_model.model_type)

    def _create_and_set_onnx_attr(self) -> None:
        """Creates Onnx model from trained model and sample input data
        and sets Card attributes
        """
        model_creator = OnnxModelCreator(
            model=self.trained_model,
            input_data=self.sample_input_data,
            additional_onnx_args=self.additional_onnx_args,
        )
        onnx_model = model_creator.create_onnx_model()
        self._set_onnx_attributes(onnx_model=onnx_model)

    def onnx_model(self) -> OnnxModelPredictor:

        """Loads a model from serialized string

        Returns
            Onnx ModelProto

        """

        if not bool(self.onnx_model_def):
            self._create_and_set_onnx_attr()

        version = self._set_version_for_predictor()

        # recast to make mypy happy
        model_def = cast(ModelDefinition, self.onnx_model_def)
        model_type = str(self.model_type)
        model_data = cast(DataDict, self.onnx_model_data)

        return OnnxModelPredictor(
            model_type=model_type,
            model_definition=model_def.model_bytes,
            data_dict=model_data,
            data_schema=self.data_schema,
            model_version=version,
        )


class PipelineCard(ArtifactCard):
    """Create a PipelineCard from specified arguments

    Args:
        name (str): Pipeline name
        team (str): Team that this card is associated with
        user_email (str): Email to associate with card
        uid (str): Unique id (assigned if card has been registered)
        version (int): Current version (assigned if card has been registered)
        pipeline_code_uri (str): Storage uri of pipeline code
        data_card_uids (dictionary): Optional dictionary of DataCard uids to associate with pipeline
        model_card_uids (dictionary): Optional dictionary of ModelCard uids to associate with pipeline
        experiment_card_uids (dictionary): Optional dictionary of ExperimentCard uids to associate with pipeline

    """

    pipeline_code_uri: Optional[str] = None
    data_card_uids: Optional[Dict[str, str]]
    model_card_uids: Optional[Dict[str, str]]
    experiment_card_uids: Optional[Dict[str, str]]

    @root_validator(pre=True)
    def set_data_uids(cls, values) -> Dict[str, Dict[str, str]]:  # pylint: disable=no-self-argument
        for uid_type in ["data_card_uids", "model_card_uids", "experiment_card_uids"]:
            if values.get(uid_type) is None:
                values[uid_type] = {}
        return values

    def add_card_uid(self, uid: str, card_type: str, name: Optional[str] = None):
        """Adds Card uid to appropriate card type attribute

        Args:
            name (str): Optional name to associate with uid
            uid (str): Card uid
            card_type (str): Card type. Accepted values are "data", "model", "experiment"
        """
        card_type = card_type.lower()
        if card_type.lower() not in ["data", "experiment", "model"]:
            raise ValueError("""Only 'model', 'experiment' and 'data' are allowed values for card_type""")

        current_ids = getattr(self, f"{card_type}_card_uids")
        new_ids = {**current_ids, **{name: uid}}
        setattr(self, f"{card_type}_card_uids", new_ids)

    def load_pipeline_code(self):
        raise NotImplementedError

    def create_registry_record(
        self,
        uid: str,
        version: int,
        registry_name: str,
        storage_client: StorageClientObj,
    ) -> PipelineRegistryRecord:
        """Creates a registry record from the current PipelineCard

        registry_name (str): PipelineCard Registry table making request
        uid (str): Unique id of PipelineCard

        """

        setattr(self, "uid", uid)
        setattr(self, "version", version)
        return PipelineRegistryRecord(**self.__dict__)


class ExperimentCard(ArtifactCard):

    """Create an ExperimentCard from specified arguments.
    Apart from required args, an Experiment card must be associated with one of data_card_uid,
    model_card_uids or pipeline_card_uid

    Args:
        name (str): Experiment name
        team (str): Team that this card is associated with
        user_email (str): Email to associate with card
        data_card_uid (str): Optional DataCard uid associated with pipeline
        model_card_uids (list): Optional List of ModelCard uids to associate with this experiment
        pipeline_card_uid (str): Optional PipelineCard uid to associate with this experiment
        metrics (dict): Optional dictionary of key (str), value (int, float) metric paris.
        Metrics can also be added via class methods.
        artifacts (dict): Optional dictionary of artifacts (i.e. plots, reports) to associate with
        the current experiment
        artifact_uris (dict): Optional dictionary of artifact uris associated with experiment artifacts.
        This is set when registering the experiment
        uid (str): Unique id (assigned if card has been registered)
        version (int): Current version (assigned if card has been registered)


    """

    data_card_uids: Optional[List[str]]
    model_card_uids: Optional[List[str]]
    pipeline_card_uid: Optional[str]
    metrics: Optional[Dict[str, Union[float, int]]]
    artifacts: Optional[Dict[str, Any]]
    artifact_uris: Optional[Dict[str, str]]
    storage_client: Optional[StorageClientObj]

    @validator("metrics", "artifacts", pre=True, always=True)
    def set_metrics(cls, value):  # pylint: disable=no-self-argument
        return value or {}

    def add_metric(self, name: str, value: Union[int, float]):
        """Adds metric to the existing ExperimentCard metric dictionary

        name (str): Name of metric
        value (float or int): Value of metric
        """

        curr_metrics = cast(Dict[str, Union[int, float]], self.metrics)
        self.metrics = {**{name: value}, **curr_metrics}

    def add_metrics(self, metrics: Dict[str, Union[float, int]]):
        """Adds metrics to the existing ExperimentCard metric dictionary

        metrics (dictionary): Dictionary containing name (str) and value (float or int) pairs
        to add to the current metric set
        """

        curr_metrics = cast(Dict[str, Union[int, float]], self.metrics)
        self.metrics = {**metrics, **curr_metrics}

    def add_artifact(self, name: str, artifact: Any):
        """Append any artifact associated with your experiment to
        the ExperimentCard. The aritfact will be saved in gcs and the uri
        will be appended to the ExperimentCard. Artifact must be pickleable
        (saved with joblib)

        Args:
            name (str): What to name the arifact
            artifact(Any): Artifact to add
        """

        curr_artifacts = cast(Dict[str, Any], self.artifacts)
        new_artifact = {name: artifact}
        self.artifacts = {**new_artifact, **curr_artifacts}
        setattr(self, "artifacts", {**new_artifact, **self.artifacts})

    def save_artifacts(self, blob_path: str, version: int) -> None:

        artifact_uris: Dict[str, str] = {}

        if self.artifacts is not None:
            save_info = SaveInfo(
                name=self.name,
                version=version,
                team=self.team,
                blob_path=blob_path,
            )
            for name, artifact in self.artifacts.items():
                storage_path = save_record_artifact_to_storage(
                    artifact=artifact,
                    save_info=save_info,
                    storage_client=cast(StorageClientObj, self.storage_client),
                )
                artifact_uris[name] = storage_path.uri
        setattr(self, "artifact_uris", artifact_uris)

    def create_registry_record(
        self,
        uid: str,
        version: int,
        registry_name: str,
        storage_client: StorageClientObj,
    ) -> ExperimentRegistryRecord:
        """Creates a registry record from the current ExperimentCard

        registry_name (str): ExperimentCardRegistry table making request
        uid (str): Unique id of ExperimentCard

        """

        if not any([self.data_card_uids, self.pipeline_card_uid, bool(self.model_card_uids)]):
            raise ValueError(
                """One of DataCard, ModelCard, or PipelineCard must be specified
            """
            )

        self._set_additional_attr(uid=uid, version=version, storage_client=storage_client)
        self.save_artifacts(blob_path=registry_name, version=version)
        return ExperimentRegistryRecord(**self.__dict__)
