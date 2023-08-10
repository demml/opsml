# pylint: disable=too-many-lines
# License: MIT

from functools import cached_property
from typing import Any, Dict, List, Optional, Union, cast

import numpy as np
import pandas as pd
import polars as pl
from pyarrow import Table
from pydantic import BaseModel, root_validator, validator

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import (
    FindPath,
    TypeChecker,
    clean_string,
    validate_name_team_pattern,
)
from opsml.model.predictor import OnnxModelPredictor
from opsml.model.types import (
    ApiDataSchemas,
    DataDict,
    ExtraOnnxArgs,
    Feature,
    InputDataType,
    ModelMetadata,
    ModelReturn,
    OnnxModelDefinition,
)
from opsml.profile.profile_data import DataProfiler, ProfileReport
from opsml.registry.cards.types import (
    METRICS,
    PARAMS,
    CardInfo,
    CardType,
    DataCardUris,
    Metric,
    ModelCardUris,
    Param,
)
from opsml.registry.data.formatter import check_data_schema
from opsml.registry.data.splitter import DataHolder, DataSplit, DataSplitter
from opsml.registry.sql.records import (
    ARBITRARY_ARTIFACT_TYPE,
    DataRegistryRecord,
    ModelRegistryRecord,
    PipelineRegistryRecord,
    ProjectRegistryRecord,
    RegistryRecord,
    RunRegistryRecord,
)
from opsml.registry.sql.settings import settings
from opsml.registry.storage.artifact_storage import load_record_artifact_from_storage
from opsml.registry.storage.types import ArtifactStorageSpecs, ArtifactStorageType

logger = ArtifactLogger.get_logger(__name__)
storage_client = settings.storage_client

SampleModelData = Optional[Union[pd.DataFrame, np.ndarray, Dict[str, np.ndarray], pl.DataFrame]]


class ArtifactCard(BaseModel):
    """Base pydantic class for artifact cards"""

    name: str
    team: str
    user_email: str
    version: Optional[str] = None
    uid: Optional[str] = None
    info: Optional[CardInfo] = None
    tags: Dict[str, str] = {}

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = False
        smart_union = True

    @root_validator(pre=True)
    def validate(cls, env_vars):
        """Validate base args and Lowercase name and team"""

        card_info = env_vars.get("info")

        for key in ["name", "team", "user_email", "version", "uid"]:
            val = env_vars.get(key)

            if card_info is not None:
                val = val or getattr(card_info, key)

            if key in ["name", "team"]:
                if val is not None:
                    val = clean_string(val)

            env_vars[key] = val

        # validate name and team for pattern
        validate_name_team_pattern(
            name=env_vars["name"],
            team=env_vars["team"],
        )

        return env_vars

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record from self attributes"""
        raise NotImplementedError

    def add_tag(self, key: str, value: str):
        self.tags[key] = str(value)

    @property
    def card_type(self) -> str:
        raise NotImplementedError


class DataCard(ArtifactCard):
    """Create a DataCard from your data.

    Args:
        data:
            Data to use for data card. Can be a pyarrow table, pandas dataframe, polars dataframe
            or numpy array
        name:
            What to name the data
        team:
            Team that this data is associated with
        user_email:
            Email to associate with data card
        dependent_vars:
            Optional list of dependent variables in data
        dependent_vars:
            List of dependent variables. Can be string or index if using numpy
        feature_descriptions:
            Dictionary of features and their descriptions
        additional_info:
            Dictionary of additional info to associate with data
            (i.e. if data is tokenized dataset, metadata could be {"vocab_size": 200})
        data_splits:
            Optional list of `DataSplit`

        runcard_uid:
            Id of RunCard that created the DataCard

        pipelinecard_uid:
            Associated PipelineCard

        sql_logic:
            Dictionary of strings containing sql logic or sql files used to create the data

        The following are non-required args and are set after registering a DataCard

        data_uri:
            Location where converted pyarrow table is stored
        version:
            DataCard version
        feature_map:
            Map of features in data (inferred when converting to pyarrow table)
        data_type:
            Data type inferred from supplied data
        uid:
            Unique id assigned to the DataCard
        data_profile:
            Optional ydata-profiling `ProfileReport`

    Returns:
        DataCard

    """

    data: Optional[Union[np.ndarray, pd.DataFrame, Table, pl.DataFrame]]
    data_splits: List[DataSplit] = []
    feature_map: Optional[Dict[str, Optional[Any]]]
    data_type: Optional[str]
    dependent_vars: Optional[List[Union[int, str]]]
    feature_descriptions: Optional[Dict[str, str]]
    additional_info: Optional[Dict[str, Union[float, int, str]]]
    sql_logic: Dict[Optional[str], Optional[str]] = {}
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    uris: DataCardUris = DataCardUris()
    data_profile: Optional[ProfileReport] = None

    @validator("uris", pre=True, always=True)
    def check_data(cls, uris: DataCardUris, values):
        if uris.data_uri is None:
            if values["data"] is None and not bool(values["sql_logic"]):
                raise ValueError("Data or sql logic must be supplied when no data_uri is present")

        return uris

    @validator("data_profile", pre=True, always=True)
    def check_profile(cls, profile):
        if profile is not None:
            from ydata_profiling import ProfileReport as ydata_profile

            assert isinstance(profile, ydata_profile)
        return profile

    @validator("feature_descriptions", pre=True, always=True)
    def lower_descriptions(cls, feature_descriptions):
        if feature_descriptions is None:
            return feature_descriptions

        feat_dict = {}
        for feature, description in feature_descriptions.items():
            feat_dict[feature.lower()] = description.lower()

        return feat_dict

    @validator("additional_info", pre=True, always=True)
    def check_info(cls, value):
        return value or {}

    @validator("sql_logic", pre=True, always=True)
    def load_sql(cls, sql_logic, values):
        if not bool(sql_logic):
            return sql_logic

        for name, query in sql_logic.items():
            if ".sql" in query:
                try:
                    sql_path = FindPath.find_filepath(name=query)
                    with open(sql_path, "r", encoding="utf-8") as file_:
                        query_ = file_.read()
                    sql_logic[name] = query_

                except Exception as error:
                    raise ValueError(f"Could not load sql file {query}. {error}") from error

        return sql_logic

    def split_data(self) -> Optional[DataHolder]:
        """
        Loops through data splits and splits data either by indexing or
        column values

        Example:

            ```python
            card_info = CardInfo(name="linnerrud", team="tutorial", user_email="user@email.com")
            data_card = DataCard(
                info=card_info,
                data=data,
                dependent_vars=["Pulse"],
                # define splits
                data_splits=[
                    {"label": "train", "indices": train_idx},
                    {"label": "test", "indices": test_idx},
                ],

            )

            splits = data_card.split_data()
            print(splits.train.X.head())

               Chins  Situps  Jumps
            0    5.0   162.0   60.0
            1    2.0   110.0   60.0
            2   12.0   101.0  101.0
            3   12.0   105.0   37.0
            4   13.0   155.0   58.0
            ```

        Returns
            Class containing data splits
        """
        if self.data is None:
            self.load_data()

        if len(self.data_splits) > 0:
            data_holder = DataHolder()
            for data_split in self.data_splits:
                label, data = DataSplitter.split(
                    split=data_split,
                    dependent_vars=self.dependent_vars,
                    data=self.data,
                )
                setattr(data_holder, label, data)

            return data_holder
        raise ValueError("No data splits provided")

    def load_data(self):
        """Loads data"""

        if self.data is None:
            storage_spec = ArtifactStorageSpecs(save_path=self.uris.data_uri)

            settings.storage_client.storage_spec = storage_spec
            data = load_record_artifact_from_storage(
                storage_client=settings.storage_client, artifact_type=self.data_type
            )
            data = check_data_schema(data, self.feature_map)

            setattr(self, "data", data)

        else:
            logger.info("Data has already been loaded")

    def create_registry_record(self) -> RegistryRecord:
        """
        Creates required metadata for registering the current data card.
        Implemented with a DataRegistry object.

        Returns:
            Registry metadata

        """
        exclude_attr = {"data"}
        return DataRegistryRecord(**self.dict(exclude=exclude_attr))

    def add_info(self, info: Dict[str, Union[float, int, str]]) -> None:
        """
        Adds metadata to the existing DataCard metadata dictionary

        Args:
            info:
                Dictionary containing name (str) and value (float, int, str) pairs
                to add to the current metadata set
        """

        curr_info = cast(Dict[str, Union[int, float, str]], self.additional_info)
        self.additional_info = {**info, **curr_info}

    def add_sql(
        self,
        name: str,
        query: Optional[str] = None,
        filename: Optional[str] = None,
    ):
        """
        Adds a query or query from file to the sql_logic dictionary. Either a query or
        a filename pointing to a sql file are required in addition to a name.

        Args:
            name:
                Name for sql query
            query:
                SQL query
            filename:
                Filename of sql query
        """
        if query is not None:
            self.sql_logic[name] = query

        elif filename is not None:
            sql_path = FindPath.find_filepath(name=filename)
            with open(sql_path, "r", encoding="utf-8") as file_:
                query = file_.read()
            self.sql_logic[name] = query

        else:
            raise ValueError("SQL Query or Filename must be provided")

    def create_data_profile(self, sample_perc: float = 1) -> ProfileReport:
        """Creates a data profile report

        Args:
            sample_perc:
                Percentage of data to use when creating a profile. Sampling is recommended for large dataframes.
                Percentage is expressed as a decimal (e.g. 1 = 100%, 0.5 = 50%, etc.)

        """

        if isinstance(self.data, (pd.DataFrame, pl.DataFrame)):
            if self.data_profile is None:
                self.data_profile = DataProfiler.create_profile_report(
                    data=self.data,
                    name=self.name,
                    sample_perc=min(sample_perc, 1),  # max of 1
                )
                return self.data_profile

            logger.info("Data profile already exists")
            return self.data_profile

        raise ValueError("A pandas dataframe type is required to create a data profile")

    @property
    def card_type(self) -> str:
        return CardType.DATACARD.value


class ModelCard(ArtifactCard):
    """Create a ModelCard from your trained machine learning model.
    This Card is used in conjunction with the ModelCardCreator class.

    Args:
        name:
            Name for the model specific to your current project
        team:
            Team that this model is associated with
        user_email:
            Email to associate with card
        trained_model:
            Trained model. Can be of type sklearn, xgboost, lightgbm or tensorflow
        sample_input_data:
            Sample of data model was trained on
        uid:
            Unique id (assigned if card has been registered)
        version:
            Current version (assigned if card has been registered)
        datacard_uid:
            Uid of the DataCard associated with training the model
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
            modelcard_uri:
                URI of modelcard
            trained_model_uri:
                URI where model is stored
            sample_data_uri:
                URI of trained model sample data
            model_metadata_uri:
                URI where model metadata is stored
    """

    trained_model: Optional[Any]
    sample_input_data: SampleModelData
    datacard_uid: Optional[str]
    onnx_model_data: Optional[DataDict]
    onnx_model_def: Optional[OnnxModelDefinition]
    sample_data_type: Optional[str]
    model_type: Optional[str]
    additional_onnx_args: Optional[ExtraOnnxArgs]
    data_schema: Optional[ApiDataSchemas]
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    to_onnx: bool = True
    uris: ModelCardUris = ModelCardUris()

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @root_validator(pre=True)
    def check_args(cls, values: Dict[str, Any]):
        """Converts trained model to modelcard"""

        if all([values.get("uid"), values.get("version")]):
            return values

        if not cls._required_args_present(values=values):
            raise ValueError(
                """trained_model and sample_input_data are required for instantiating a ModelCard""",
            )

        return values

    @validator("sample_input_data", pre=True)
    def get_one_sample(cls, input_data: SampleModelData) -> SampleModelData:
        """Parses input data and returns a single record to be used during ONNX conversion and validation"""

        if input_data is None:
            return input_data

        if not isinstance(input_data, InputDataType.DICT.value):
            if isinstance(input_data, InputDataType.POLARS_DATAFRAME.value):
                input_data = input_data.to_pandas()

            return input_data[0:1]

        sample_dict = {}
        if isinstance(input_data, dict):
            for key in input_data.keys():
                sample_dict[key] = input_data[key][0:1]

            return sample_dict

        raise ValueError("Provided sample data is not a valid type")

    @classmethod
    def _required_args_present(cls, values: Dict[str, Any]) -> bool:
        return all(
            values.get(var_) is not None
            for var_ in [
                "trained_model",
                "sample_input_data",
            ]
        )

    @property
    def model_data_schema(self) -> DataDict:
        if self.data_schema is not None:
            return self.data_schema.model_data_schema
        raise ValueError("Model data schema has not been set")

    @property
    def input_data_schema(self) -> Dict[str, Feature]:
        if self.data_schema is not None and self.data_schema.input_data_schema is not None:
            return self.data_schema.input_data_schema
        raise ValueError("Model input data schema has not been set or is not needed for this model")

    def load_sample_data(self):
        """Loads sample data associated with original non-onnx model"""

        storage_spec = ArtifactStorageSpecs(save_path=self.uris.sample_data_uri)

        storage_client.storage_spec = storage_spec
        sample_data = load_record_artifact_from_storage(
            storage_client=storage_client,
            artifact_type=self.sample_data_type,
        )

        setattr(self, "sample_input_data", sample_data)

    def load_trained_model(self):
        """Loads original trained model"""

        if not all([bool(self.uris.trained_model_uri), bool(self.uris.sample_data_uri)]):
            raise ValueError(
                """Trained model uri and sample data uri must both be set to load a trained model""",
            )

        if self.trained_model is None:
            self.load_sample_data()
            storage_spec = ArtifactStorageSpecs(save_path=self.uris.trained_model_uri)
            storage_client.storage_spec = storage_spec

            trained_model = load_record_artifact_from_storage(
                storage_client=storage_client,
                artifact_type=self.model_type,
            )

            setattr(self, "trained_model", trained_model)

    @property
    def model_metadata(self) -> ModelMetadata:
        """Loads `ModelMetadata` class"""
        storage_spec = ArtifactStorageSpecs(save_path=self.uris.model_metadata_uri)
        storage_client.storage_spec = storage_spec
        model_metadata = load_record_artifact_from_storage(
            storage_client=storage_client,
            artifact_type=ArtifactStorageType.JSON.value,
        )

        return ModelMetadata.parse_obj(model_metadata)

    def _load_onnx_model(self, metadata: ModelMetadata) -> Any:
        """Loads the actual onnx file

        Args:
            metadata:
                `ModelMetadata`
        """
        if metadata.onnx_uri is not None:
            storage_client.storage_spec.save_path = metadata.onnx_uri
            onnx_model = load_record_artifact_from_storage(
                storage_client=storage_client,
                artifact_type=ArtifactStorageType.ONNX.value,
            )

            return onnx_model

        raise ValueError("Onnx uri is not specified")

    def load_onnx_model_definition(self) -> None:
        """Loads the onnx model definition"""

        if self.uris.model_metadata_uri is None:
            raise ValueError("No model metadata exists. Please check the registry or register a new model")

        metadata = self.model_metadata
        onnx_model = self._load_onnx_model(metadata=metadata)

        model_def = OnnxModelDefinition(
            onnx_version=metadata.onnx_version,
            model_bytes=onnx_model.SerializeToString(),
        )

        setattr(self, "onnx_model_def", model_def)

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record from the current ModelCard"""

        exclude_vars = {"trained_model", "sample_input_data", "onnx_model_def"}
        return ModelRegistryRecord(**self.dict(exclude=exclude_vars))

    def _set_version_for_predictor(self) -> str:
        if self.version is None:
            logger.warning("""ModelCard has no version (not registered). Defaulting to 1 (for testing only)""")
            version = "1.0.0"
        else:
            version = self.version

        return version

    def _set_model_attributes(self, model_return: ModelReturn) -> None:
        setattr(self, "onnx_model_def", model_return.model_definition)
        setattr(self, "data_schema", model_return.api_data_schema)
        setattr(self, "model_type", model_return.model_type)

    def _create_and_set_model_attr(self) -> None:
        """
        Creates Onnx model from trained model and sample input data
        and sets Card attributes

        """

        from opsml.model.creator import (  # pylint: disable=import-outside-toplevel
            create_model,
        )

        model_return = create_model(
            model=self.trained_model,
            input_data=self.sample_input_data,
            additional_onnx_args=self.additional_onnx_args,
            to_onnx=self.to_onnx,
            onnx_model_def=self.onnx_model_def,
        )

        self._set_model_attributes(model_return=model_return)

    def _get_sample_data_for_api(self) -> Dict[str, Any]:
        """
        Converts sample data to dictionary that can be used
        to validate an onnx model
        """

        if self.sample_input_data is None:
            self.load_sample_data()

        sample_data = cast(
            Union[pd.DataFrame, np.ndarray, Dict[str, Any]],
            self.sample_input_data,
        )

        if isinstance(sample_data, np.ndarray):
            model_data = self.model_data_schema
            input_name = next(iter(model_data.input_features.keys()))
            return {input_name: sample_data[0, :].tolist()}

        if isinstance(sample_data, pd.DataFrame):
            record = list(sample_data[0:1].T.to_dict().values())[0]
            return record

        if isinstance(sample_data, pl.DataFrame):
            record = list(sample_data.to_pandas()[0:1].T.to_dict().values())[0]
            return record

        record = {}
        for feat, val in sample_data.items():
            record[feat] = np.ravel(val).tolist()
        return record

    def onnx_model(self, start_onnx_runtime: bool = True) -> OnnxModelPredictor:
        """
        Loads an onnx model from string or creates an onnx model from trained model

        Args:
            start_onnx_runtime:
                Whether to start the onnx runtime session or not

        Returns
            `OnnxModelPredictor`

        """

        # todo: clean this up
        if self.onnx_model_def is None or self.data_schema is None:
            self._create_and_set_model_attr()

        version = self._set_version_for_predictor()

        # recast to make mypy happy
        # todo: refactor
        model_def = cast(OnnxModelDefinition, self.onnx_model_def)
        model_type = str(self.model_type)
        data_schema = cast(ApiDataSchemas, self.data_schema)

        sample_api_data = self._get_sample_data_for_api()

        return OnnxModelPredictor(
            model_name=self.name,
            model_type=model_type,
            model_definition=model_def.model_bytes,
            data_schema=data_schema,
            model_version=version,
            onnx_version=model_def.onnx_version,
            sample_api_data=sample_api_data,
            start_sess=start_onnx_runtime,
        )

    @property
    def card_type(self) -> str:
        return CardType.MODELCARD.value


class PipelineCard(ArtifactCard):
    """Create a PipelineCard from specified arguments

    Args:
        name:
            Pipeline name
        team:
            Team that this card is associated with
        user_email:
            Email to associate with card
        uid:
            Unique id (assigned if card has been registered)
        version:
            Current version (assigned if card has been registered)
        pipeline_code_uri:
            Storage uri of pipeline code
        datacard_uids:
            Optional list of DataCard uids to associate with pipeline
        modelcard_uids:
            Optional list of ModelCard uids to associate with pipeline
        runcard_uids:
            Optional list of RunCard uids to associate with pipeline

    """

    pipeline_code_uri: Optional[str] = None
    datacard_uids: List[Optional[str]] = []
    modelcard_uids: List[Optional[str]] = []
    runcard_uids: List[Optional[str]] = []

    def add_card_uid(self, uid: str, card_type: str):
        """
        Adds Card uid to appropriate card type attribute

        Args:
            uid:
                Card uid
            card_type:
                Card type. Accepted values are "data", "model", "run"
        """
        card_type = card_type.lower()
        if card_type.lower() not in [CardType.DATACARD.value, CardType.RUNCARD.value, CardType.MODELCARD.value]:
            raise ValueError("""Only 'model', 'run' and 'data' are allowed values for card_type""")

        current_ids = getattr(self, f"{card_type}card_uids")
        new_ids = [*current_ids, *[uid]]
        setattr(self, f"{card_type}card_uids", new_ids)

    def load_pipeline_code(self):
        raise NotImplementedError

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record from the current PipelineCard"""
        return PipelineRegistryRecord(**self.dict())

    @property
    def card_type(self) -> str:
        return CardType.PIPELINECARD.value


class RunCard(ArtifactCard):

    """
    Create a RunCard from specified arguments.

    Apart from required args, a RunCard must be associated with one of
    datacard_uid, modelcard_uids or pipelinecard_uid

    Args:
        name:
            Run name
        team:
            Team that this card is associated with
        user_email:
            Email to associate with card
        datacard_uid:
            Optional DataCard uid associated with pipeline
        modelcard_uids:
            Optional List of ModelCard uids to associate with this run
        pipelinecard_uid:
            Optional PipelineCard uid to associate with this experiment
        metrics:
            Optional dictionary of key (str), value (int, float) metric paris.
            Metrics can also be added via class methods.
        parameters:
            Parameters associated with a RunCard
        artifacts:
            Optional dictionary of artifacts (i.e. plots, reports) to associate
            with the current run.
        artifact_uris:
            Optional dictionary of artifact uris associated with artifacts.
        uid:
            Unique id (assigned if card has been registered)
        version:
            Current version (assigned if card has been registered)

    """

    datacard_uids: List[str] = []
    modelcard_uids: List[str] = []
    pipelinecard_uid: Optional[str]
    metrics: METRICS = {}
    parameters: PARAMS = {}
    artifacts: Dict[str, Any] = {}
    artifact_uris: Dict[str, str] = {}
    tags: Dict[str, str] = {}
    project_id: Optional[str]
    runcard_uri: Optional[str]

    def add_tag(self, key: str, value: str):
        """
        Logs params to current RunCard

        Args:
            key:
                Key for tag
            value:
                value for tag
        """
        self.tags = {**{key: value}, **self.tags}

    def add_tags(self, tags: Dict[str, str]):
        """
        Logs params to current RunCard

        Args:
            tags:
                Dictionary of tags
        """
        self.tags = {**tags, **self.tags}

    def log_parameters(self, params: Dict[str, Union[float, int, str]]):
        """
        Logs params to current RunCard

        Args:
            params:
                Dictionary of parameters
        """

        for key, value in params.items():
            # check key
            self.log_parameter(key, value)

    def log_parameter(self, key: str, value: Union[int, float, str]):
        """
        Logs params to current RunCard

        Args:
            key:
                Param name
            value:
                Param value
        """

        TypeChecker.check_param_type(param=value)
        param = Param(name=key, value=value)

        if self.parameters.get(key) is not None:
            self.parameters[key].append(param)

        else:
            self.parameters[key] = [param]

    def log_metric(
        self,
        key: str,
        value: Union[int, float],
        timestamp: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        """
        Logs metric to the existing RunCard metric dictionary

        Args:
            key:
                Metric name
            value:
                Metric value
            timestamp:
                Optional timestamp
            step:
                Optional step associated with name and value
        """

        TypeChecker.check_metric_type(metric=value)
        metric = Metric(name=key, value=value, timestamp=timestamp, step=step)

        if self.metrics.get(key) is not None:
            self.metrics[key].append(metric)
        else:
            self.metrics[key] = [metric]

    def log_metrics(self, metrics: Dict[str, Union[float, int]], step: Optional[int] = None) -> None:
        """
        Log metrics to the existing RunCard metric dictionary

        Args:
            metrics:
                Dictionary containing key (str) and value (float or int) pairs
                to add to the current metric set
            step:
                Optional step associated with metrics
        """

        for key, value in metrics.items():
            self.log_metric(key, value, step)

    def log_artifact(self, name: str, artifact: Any) -> None:
        """
        Append any artifact associated with your run to
        the RunCard. The artifact will be saved and the uri
        will be appended to the RunCard. Artifact must be pickleable
        (saved with joblib)

        Args:
            name:
                Artifact name
            artifact:
                Artifact
        """

        curr_artifacts = cast(Dict[str, Any], self.artifacts)
        new_artifact = {name: artifact}
        self.artifacts = {**new_artifact, **curr_artifacts}
        setattr(self, "artifacts", {**new_artifact, **self.artifacts})

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record from the current RunCard"""

        exclude_attr = {"artifacts", "params", "metrics"}

        return RunRegistryRecord(**self.dict(exclude=exclude_attr))

    def add_artifact_uri(self, name: str, uri: str):
        """
        Adds an artifact_uri to the runcard

        Args:
            name:
                Name to associate with artifact
            uri:
                Uri where artifact is stored
        """

        self.artifact_uris[name] = uri

    def add_card_uid(self, card_type: str, uid: str) -> None:
        """
        Adds a card uid to the appropriate card uid list for tracking

        Args:
            card_type:
                ArtifactCard class name
            uid:
                Uid of registered ArtifactCard
        """

        if card_type == CardType.DATACARD:
            self.datacard_uids = [uid, *self.datacard_uids]
        elif card_type == CardType.MODELCARD:
            self.modelcard_uids = [uid, *self.modelcard_uids]

    def get_metric(self, name: str) -> Union[List[Metric], Metric]:
        """
        Gets a metric by name

        Args:
            name:
                Name of metric

        Returns:
            List of dictionaries or dictionary containing value

        """
        metric = self.metrics.get(name)
        if metric is not None:
            if len(metric) > 1:
                return metric
            if len(metric) == 1:
                return metric[0]
            return metric

        raise ValueError(f"Metric {metric} is not defined")

    def get_parameter(self, name: str) -> Union[List[Param], Param]:
        """
        Gets a metric by name

        Args:
            name:
                Name of param

        Returns:
            List of dictionaries or dictionary containing value

        """
        param = self.parameters.get(name)
        if param is not None:
            if len(param) > 1:
                return param
            if len(param) == 1:
                return param[0]
            return param

        raise ValueError(f"Param {param} is not defined")

    def load_artifacts(self) -> None:
        if bool(self.artifact_uris):
            for name, uri in self.artifact_uris.items():
                storage_spec = ArtifactStorageSpecs(save_path=uri)
                storage_client.storage_spec = storage_spec
                self.artifacts[name] = load_record_artifact_from_storage(
                    storage_client=storage_client,
                    artifact_type=ARBITRARY_ARTIFACT_TYPE,
                )
            return None

        logger.info("No artifact uris associated with RunCard")
        return None

    @property
    def card_type(self) -> str:
        return CardType.RUNCARD.value


class ProjectCard(ArtifactCard):
    """
    Card containing project information
    """

    project_id: Optional[str] = None

    @validator("project_id", pre=True, always=True)
    def create_project_id(cls, value, values, **kwargs):
        return f'{values["name"]}:{values["team"]}'

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record for a project"""

        return ProjectRegistryRecord(**self.dict())

    @property
    def card_type(self) -> str:
        return CardType.PROJECTCARD.value
