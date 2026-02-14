#### begin imports ####

import datetime
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    TypeAlias,
    TypeVar,
    Union,
    overload,
)

from .genai.potato import *
from .opsml import (
    Data,
    DataInterface,
    DataLoadKwargs,
    DataProfile,
    DataSaveKwargs,
    DataType,
    DeploymentConfig,
    DriftConfig,
    DriftProfileMap,
    FeatureSchema,
    GenAIEvalProfile,
    ModelInterface,
    ModelLoadKwargs,
    ModelSaveKwargs,
    OnnxSession,
    Prompt,
    PromptSaveKwargs,
    ServiceConfig,
    ServiceMetadata,
)
from .scouter.evaluate import *
from .scouter.scouter import *
from .types import VersionType

CardInterfaceType: TypeAlias = Union["DataInterface", "ModelInterface"]
ServiceCardInterfaceType: TypeAlias = Dict[str, Union["DataInterface", "ModelInterface"]]
LoadInterfaceType: TypeAlias = Union[ServiceCardInterfaceType, ServiceCardInterfaceType]
#### end of imports ####

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Experiment: "RegistryType"
    Audit: "RegistryType"
    Prompt: "RegistryType"
    Service: "RegistryType"

class RegistryMode:
    Client: "RegistryMode"
    Server: "RegistryMode"

class ServiceType:
    """
    Enum representing the type of service.

    Attributes:
        Api: REST API service
        Mcp: Model Context Protocol service
        Agent: Agentic workflow service
    """

    Api: "ServiceType"
    Mcp: "ServiceType"
    Agent: "ServiceType"

class CardRecord:
    uid: Optional[str]
    created_at: Optional[str]
    app_env: Optional[str]
    name: str
    space: str
    version: str
    tags: Dict[str, str]
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    experimentcard_uids: Optional[List[str]]
    auditcard_uid: Optional[str]
    interface_type: Optional[str]
    data_type: Optional[str]
    model_type: Optional[str]
    task_type: Optional[str]

    def __str__(self) -> str:
        """Return a string representation of the Card.

        Returns:
            String representation of the Card.
        """

class CardList:
    cards: List[CardRecord]

    def __getitem__(self, key: int) -> Optional[CardRecord]:
        """Return the card at the specified index"""

    def __iter__(self) -> CardRecord:
        """Return an iterator for the card list"""

    def as_table(self) -> None:
        """Print cards as a table"""

    def __len__(self) -> int:
        """Return the length of the card list"""

# Registry

class DataCard:
    def __init__(  # pylint: disable=dangerous-default-value
        self,
        interface: Optional[DataInterface] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Define a data card

        Args:
            interface (DataInterface | None):
                The data interface
            space (str | None):
                The space of the card
            name (str | None):
                The name of the card
            version (str | None):
                The version of the card
            uid (str | None):
                The uid of the card
            tags (List[str]):
                The tags of the card

        Example:
        ```python
        from opsml import DataCard, CardRegistry, RegistryType, PandasData

        # for testing purposes
        from opsml.helpers.data import create_fake_data

        # pandas data
        X, _ = create_fake_data(n_samples=1200)

        interface = PandasData(data=X)
        datacard = DataCard(
            interface=interface,
            space="my-repo",
            name="my-name",
            tags=["foo:bar", "baz:qux"],
        )

        # register card
        registry = CardRegistry(RegistryType.Data)
        registry.register_card(datacard)
        ```
        """

    @property
    def data(self) -> Any:
        """Return the data. This is a special property that is used to
        access the data from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the data
        has not been loaded.
        """

    @property
    def experimentcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: Optional[str]) -> None:
        """Set the experimentcard uid"""

    @property
    def interface(self) -> Optional[DataInterface]:
        """Return the data interface"""

    @interface.setter
    def interface(self, interface: Any) -> None:
        """Set the data interface

        Args:
            interface (DataInterface):
                The data interface to set. Must inherit from DataInterface
        """

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the created at timestamp"""

    @property
    def name(self) -> str:
        """Return the name of the data card"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the data card

        Args:
            name (str):
                The name of the data card
        """

    @property
    def space(self) -> str:
        """Return the space of the data card"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the data card

        Args:
            space (str):
                The space of the data card
        """

    @property
    def version(self) -> str:
        """Return the version of the data card"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the data card

        Args:
            version (str):
                The version of the data card
        """

    @property
    def uid(self) -> str:
        """Return the uid of the data card"""

    @property
    def tags(self) -> List[str]:
        """Return the tags of the data card"""

    @tags.setter
    def tags(self, tags: List[str]) -> None:
        """Set the tags of the data card

        Args:
            tags (List[str]):
                The tags of the data card
        """

    @property
    def metadata(self) -> "DataCardMetadata":  # pylint: disable=used-before-assignment
        """Return the metadata of the data card"""

    @property
    def registry_type(self) -> "RegistryType":
        """Return the card type of the data card"""

    @property
    def data_type(self) -> "DataType":
        """Return the data type"""

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> None:
        """Save the data card

        Args:
            path (Path):
                The path to save the data card to
            save_kwargs (DataSaveKwargs | None):
                Optional save kwargs to that will be passed to the
                data interface save method

        Acceptable save kwargs:
            Kwargs are passed to the underlying data interface for saving.
            For a complete list of options see the save method of the data interface and
            their associated libraries.
        """

    def load(
        self,
        path: Optional[Path] = None,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data card

        Args:
            path (Path | None):
                The path to load the data card from. If no path is provided,
                the data interface will be loaded from the server.
            load_kwargs (DataLoadKwargs | None):
                Optional load kwargs to that will be passed to the
                data interface load method
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with the DataCard

        Args:
            path (Path):
                Path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "card_artifacts"
        """

    def model_dump_json(self) -> str:
        """Return the model dump as a json string"""

    @staticmethod
    def model_validate_json(json_string: str, interface: Optional[DataInterface] = None) -> "ModelCard":
        """Validate the model json string

        Args:
            json_string (str):
                The json string to validate
            interface (DataInterface):
                By default, the interface will be inferred and instantiated
                from the interface metadata. If an interface is provided
                (as in the case of custom interfaces), it will be used.
        """

    def create_data_profile(
        self,
        bin_size: Optional[int] = 20,
        compute_correlations: Optional[bool] = False,
    ) -> DataProfile:
        """Create a data profile


        Args:
            bin_size (int):
                The bin size for the data profile
            compute_correlations (bool):
                Whether to compute correlations
        """

    def split_data(self) -> Dict[str, Data]:
        """Split the data according to the data splits defined in the interface

        Returns:
            Dict[str, Any]:
                A dictionary containing the split data
        """

class DataCardMetadata:
    @property
    def schema(self) -> "FeatureSchema":
        """Return the feature map"""

    @property
    def experimentcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

    @property
    def auditcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

class ModelCardMetadata:
    def __init__(
        self,
        datacard_uid: Optional[str] = None,
        experimentcard_uid: Optional[str] = None,
        auditcard_uid: Optional[str] = None,
    ) -> None:
        """Create a ModelCardMetadata object

        Args:
            datacard_uid (str | None):
                The datacard uid
            experimentcard_uid (str | None):
                The experimentcard uid
            auditcard_uid (str | None):
                The auditcard uid
        """

    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def auditcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @auditcard_uid.setter
    def auditcard_uid(self, auditcard_uid: str) -> None:
        """Set the experimentcard uid"""

class ModelCard:
    def __init__(
        self,
        interface: Optional[ModelInterface] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
        datacard_uid: Optional[str] = None,
        metadata: ModelCardMetadata = ModelCardMetadata(),
    ) -> None:
        """Create a ModelCard from a machine learning model.

        Cards are stored in the ModelCardRegistry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}

        Args:
            interface (ModelInterface | None):
                `ModelInterface` class containing trained model
            space (str | None):
                space to associate with `ModelCard`
            name (str | None):
                Name to associate with `ModelCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `ModelCard`. Can be a dictionary of strings or
                a `Tags` object.
            datacard_uid (str | None):
                The datacard uid to associate with the model card. This is used to link the
                model card to the data card. Datacard uid can also be set in card metadata.
            metadata (ModelCardMetadata):
                Metadata to associate with the `ModelCard. Defaults to an empty `ModelCardMetadata` object.

        Example:
        ```python
        from opsml import ModelCard, CardRegistry, RegistryType, SklearnModel, TaskType
        from sklearn import ensemble

        # for testing purposes
        from opsml.helpers.data import create_fake_data

        # pandas data
        X, y = create_fake_data(n_samples=1200)

        # train model
        reg = ensemble.RandomForestClassifier(n_estimators=5)
        reg.fit(X_train.to_numpy(), y_train)

        # create interface and card
        interface = SklearnModel(
            model=reg,
            sample_data=X_train,
            task_type=TaskType.Classification,
        )

        modelcard = ModelCard(
            interface=random_forest_classifier,
            space="my-repo",
            name="my-model",
            tags=["foo:bar", "baz:qux"],
        )

        # register card
        registry = CardRegistry(RegistryType.Model, save_kwargs=ModelSaveKwargs(save_onnx=True)) # convert to onnx
        registry.register_card(modelcard)
        ```
        """

    @property
    def model(self) -> Any:
        """Returns the model. This is a special property that is used to
        access the model from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the model
        has not been loaded.
        """

    @property
    def onnx_session(self) -> Optional[OnnxSession]:
        """Returns the onnx session. This is a special property that is used to
        access the onnx session from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the model
        has not been loaded.
        """

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the created at timestamp"""

    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def uri(self) -> Path:
        """Returns the uri of the `ModelCard` in the
        format of {registry}/{space}/{name}/v{version}
        """

    @property
    def interface(self) -> Optional[ModelInterface]:
        """Returns the `ModelInterface` associated with the `ModelCard`"""

    @interface.setter
    def interface(self, interface: Any) -> None:
        """Set the `ModelInterface` associated with the `ModelCard`"""

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `ModelCard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `ModelCard`

        Args:
            space (str):
                The space of the `ModelCard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `ModelCard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `ModelCard`

        Args:
            version (str):
                The version of the `ModelCard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `ModelCard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ModelCard`"""

    @property
    def metadata(self) -> ModelCardMetadata:
        """Returns the metadata of the `ModelCard`"""

    @property
    def registry_type(self) -> RegistryType:
        """Returns the card type of the `ModelCard`"""

    def save(self, path: Path, save_kwargs: Optional[ModelSaveKwargs] = None) -> None:
        """Save the model card to a directory

        Args:
            path (Path):
                Path to save the model card.
            save_kwargs (SaveKwargs):
                Optional kwargs to pass to `ModelInterface` save method.
        """

    def load(
        self,
        path: Optional[Path] = None,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelCard interface components

        Args:
            path (Path | None):
                The path to load the data card from. If no path is provided,
                the model interface will be loaded from the server.
            load_kwargs (ModelLoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
        """

    @staticmethod
    def load_from_path(
        path: Path,
        load_kwargs: None | ModelLoadKwargs = None,
        interface: Optional[ModelInterface] = None,
    ) -> "ModelCard":
        """Staticmethod to load a ModelCard from a path. Typically used when
        a `ModelCard`s artifacts have already been downloaded to a path.

        This is commonly used in API workflows where a user may download artifacts to
        a directory and load the contents during API/Application startup.

        Args:
            path (Path):
                The path to load the ModelCard from.
            load_kwargs (ModelLoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
            interface (ModelInterface):
                Optional interface for the model. Used with Custom interfaces.

        Returns:
            ModelCard:
                The loaded ModelCard.

        Example:

            ```python
            # shell command
            opsml run get model --space <space_name> --name <model_name> --write-dir <path>

            # Within python application
            model_card = ModelCard.load_from_path(<path>)
            ```
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with the ModelCard

        Args:
            path (Path):
                Path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "card_artifacts"
        """

    def model_dump_json(self) -> str:
        """Return the model dump as a json string"""

    @staticmethod
    def model_validate_json(json_string: str, interface: Optional[ModelInterface] = None) -> "ModelCard":
        """Validate the model json string

        Args:
            json_string (str):
                The json string to validate
            interface (ModelInterface):
                By default, the interface will be inferred and instantiated
                from the interface metadata. If an interface is provided
                (as in the case of custom interfaces), it will be used.
        """

    def drift_profile_path(self, alias: str) -> Path:
        """Helper method that returns the path to a specific drift profile.
        This method will fail if there is no drift profile map or the alias
        does not exist.

        Args:
            alias (str):
                The alias of the drift profile

        Returns:
            Path to the drift profile
        """

    def __str__(self) -> str:
        """Return a string representation of the ModelCard.

        Returns:
            String representation of the ModelCard.
        """

    @property
    def drift_profile(self) -> "DriftProfileMap":
        """Return the drift profile map from the model interface.

        Returns:
            DriftProfileMap
        """

class ComputeEnvironment:
    cpu_count: int
    total_memory: int
    total_swap: int
    system: str
    os_version: str
    hostname: str
    python_version: str

    def __str__(self): ...

class UidMetadata:
    datacard_uids: List[str]
    modelcard_uids: List[str]
    promptcard_uids: List[str]
    service_card_uids: List[str]
    experimentcard_uids: List[str]

class ExperimentCard:
    def __init__(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Instantiates a ExperimentCard.

        Cards are stored in the ExperimentCard Registry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}

        Args:
            space (str | None):
                space to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `ExperimentCard`. Can be a dictionary of strings or
                a `Tags` object.

        Example:
        ```python
        from opsml import start_experiment

        # start an experiment
        with start_experiment(space="test", log_hardware=True) as exp:
            exp.log_metric("accuracy", 0.95)
            exp.log_parameter("epochs", 10)
        ```
        """

    def get_metrics(
        self,
        names: Optional[list[str]] = None,
    ) -> Metrics:
        """
        Get metrics of an experiment

        Args:
            names (list[str] | None):
                Names of the metrics to get. If None, all metrics will be returned.

        Returns:
            Metrics
        """

    def get_parameters(
        self,
        names: Optional[list[str]] = None,
    ) -> "Parameters":
        """
        Get parameters of an experiment

        Args:
            names (list[str] | None):
                Names of the parameters to get. If None, all parameters will be returned.

        Returns:
            Parameters
        """

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `experimentcard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `experimentcard`

        Args:
            space (str):
                The space of the `experimentcard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `experimentcard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `experimentcard`

        Args:
            version (str):
                The version of the `experimentcard`
        """

    @property
    def eval_metrics(self) -> "EvalMetrics":
        """Returns the eval metrics of the `experimentcard`"""

    @eval_metrics.setter
    def eval_metrics(self, metrics: "EvalMetrics") -> None:
        """Set the eval metrics of the `experimentcard`

        Args:
            metrics (EvalMetrics):
                The eval metrics of the `experimentcard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `experimentcard`"""

    @property
    def uids(self) -> UidMetadata:
        """Returns the uids of the `experimentcard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ExperimentCard`"""

    @property
    def artifacts(self) -> List[str]:
        """Returns the artifact names"""

    @property
    def compute_environment(self) -> ComputeEnvironment:
        """Returns the compute env"""

    @property
    def registry_type(self) -> RegistryType:
        """Returns the card type of the `experimentcard`"""

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the created at timestamp"""

    def add_child_experiment(self, uid: str) -> None:
        """Add a child experiment to the experiment card

        Args:
            uid (str):
                The experiment card uid to add
        """

    def list_artifacts(self, path: Optional[Path]) -> List[str]:
        """List the artifacts associated with the experiment card

        Args:
            path (Path):
                Specific path you wish to list artifacts from. If not provided,
                all artifacts will be listed.

                Example:
                    You logged artifacts with the following paths:
                    - "data/processed/my_data.csv"
                    - "model/my_model.pkl"

                    If you wanted to list all artifacts in the "data" directory,
                    you would pass Path("data") as the path.
        """

    def download_artifacts(
        self,
        path: Optional[Path] = None,
        lpath: Optional[Path] = None,
    ) -> None:
        """Download artifacts associated with the ExperimentCard

        Args:
            path (Path | None):
                Specific path you wish to download artifacts from. If not provided,
                all artifacts will be downloaded.

            lpath (Path | None):
                Local path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "artifacts"
        """

    def download_artifact(
        self,
        path: Path,
        lpath: Optional[Path] = None,
    ) -> None:
        """Download a specific artifact associated with the ExperimentCard

        Args:
            path (Path):
                Path to the artifact to download
            lpath (Path | None):
                Local path to save the artifact. If not provided, the artifact will be saved
                to a directory called "artifacts"

        Examples:

        ```python
        # artifact logged to artifacts/data.csv
        download_artifact(Path("artifacts/data.csv"))
        #or
        download_artifact(Path("data.csv"))
        ```
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "ExperimentCard":
        """Load card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def __str__(self) -> str:
        """Return a string representation of the `ExperimentCard`.

        Returns:
            String representation of the ModelCard.
        """

class PromptCard:
    def __init__(
        self,
        prompt: Prompt,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
        eval_profile: Optional[Dict[str, GenAIEvalProfile] | List[GenAIEvalProfile] | GenAIEvalProfile] = None,
    ) -> None:
        """Creates a `PromptCard`.

        Cards are stored in the PromptCard Registry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}


        Args:
            prompt (Prompt):
                Prompt to associate with `PromptCard`
            space (str | None):
                space to associate with `PromptCard`
            name (str | None):
                Name to associate with `PromptCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `PromptCard`. Can be a dictionary of strings or
                a `Tags` object.
            drift_profile:
                Drift profile(s) to associate with the prompt. Must be a dictionary of
                alias and drift profile, a list of drift profiles with aliases, or a single drift profile with an alias.
        Example:
        ```python
        from opsml import Prompt, PromptCard, CardRegistry, RegistryType

        # create prompt
        prompt = Prompt(
            model="openai:gpt-4o",
            messages=[
                "My prompt $1 is $2",
                "My prompt $3 is $4",
            ],
            system_instructions="system_prompt",
        )

        # create card
        card = PromptCard(
            prompt=prompt,
            space="my-repo",
            name="my-prompt",
            version="0.0.1",
            tags=["gpt-4o", "prompt"],
        )

        # register card
        registry = CardRegistry(RegistryType.Prompt)
        registry.register_card(card)
        ```
        """

    @property
    def prompt(self) -> Prompt:
        """Returns the prompt"""

    @prompt.setter
    def prompt(self, prompt: Prompt) -> None:
        """Set the prompt

        Args:
            prompt (Prompt):
                The prompt to set
        """

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `ModelCard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `ModelCard`

        Args:
            space (str):
                The space of the `ModelCard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `ModelCard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `ModelCard`

        Args:
            version (str):
                The version of the `ModelCard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `ModelCard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ModelCard`"""

    def save(self, path: Path) -> None:
        """Save the `PromptCard` to a directory

        Args:
            path (Path):
                Path to save the prompt card.
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "PromptCard":
        """Load card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def __str__(self): ...
    def create_eval_profile(
        self,
        alias: str,
        tasks: Sequence[LLMJudgeTask | AssertionTask | TraceAssertionTask],
        config: Optional[GenAIEvalConfig] = None,
    ) -> None:
        """Initialize a GenAIEvalProfile for LLM evaluation and drift detection.

        LLM evaluations are run asynchronously on the scouter server.

        Overview:
            GenAI evaluations are defined using assertion tasks and LLM judge tasks.
            Assertion tasks evaluate specific metrics based on model responses, and do not require
            the use of an LLM judge or extra call. It is recommended to use assertion tasks whenever possible
            to reduce cost and latency. LLM judge tasks leverage an additional LLM call to evaluate
            model responses based on more complex criteria. Together, these tasks provide a flexible framework
            for monitoring LLM performance and detecting drift over time.


        Args:
            alias (str):
                Unique alias for the drift profile within the prompt card.

            tasks (List[LLMJudgeTask | AssertionTask | TraceAssertionTask]):
                List of evaluation tasks to include in the profile. Can contain
                a mix of LLM judge tasks, assertion tasks, and trace assertion tasks.

            config (GenAIEvalConfig | None):
                The configuration for the GenAI drift profile containing space, name,
                version, and alert settings.

        Returns:
            GenAIEvalProfile: Configured profile ready for GenAI drift monitoring.

        Raises:
            ProfileError: If workflow validation fails, metrics are empty when no
                workflow is provided, or if workflow tasks don't match metric names.

        Examples:
            Basic usage with metrics only:

            >>> config = GenAIEvalConfig("my_space", "my_model", "1.0")
            >>>  tasks = [
            ...     LLMJudgeTask(
            ...         id="response_relevance",
            ...         prompt=relevance_prompt,
            ...         expected_value=7,
            ...         field_path="score",
            ...         operator=ComparisonOperator.GreaterThanOrEqual,
            ...         description="Ensure relevance score >= 7"
            ...     )
            ... ]
            >>> profile = Drifter().create_genai_drift_profile(config, tasks)

        """

    @property
    def eval_profile(self) -> "DriftProfileMap":
        """Return the drift profile map from the model interface.

        Returns:
            DriftProfileMap
        """

    @eval_profile.setter
    def eval_profile(self, eval_profile: "DriftProfileMap") -> None:
        """Set the drift profile map for the prompt card.

        Args:
            eval_profile (DriftProfileMap):
                The drift profile map to set.
        """

class Card:
    """Represents a card from a given registry that can be used in a service card"""

    def __init__(
        self,
        alias: str,
        registry_type: Optional[RegistryType] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        card: Optional["CardT"] = None,
        drift: Optional[DriftConfig] = None,
    ) -> None:
        """Initialize the service card. Card accepts either a combination of
        space and name (with version as optional) or a uid. If only space and name are
        provided with no version, the latest version for a given space and name will be used
        (e.g. {space}/{name}/v*). If a version is provided, it must follow semver rules that
        are compatible with opsml (e.g. v1.*, v1.2.3, v2.3.4-alpha, etc.). If both space/name and uid
        are provided, the uid will take precedence. If neither space/name nor uid are provided,
        an error will be raised.

        Alias is used to identify the card in the service card and is not necessarily the name of
        the card. It is recommended to use a short and descriptive alias that is easy to remember.

        Example:

        ```python
        service = ServiceCard(...)
        service["my_alias"]
        ```


        Args:
            alias (str):
                The alias of the card
            registry_type (RegistryType):
                The type of registry the service card belongs to. This is
                required if no card is provided.
            space (str):
                The space of the service card
            name (str):
                The name of the service card
            version (str):
                The version of the service card
            uid (str):
                The uid of the service card
            card (Union[DataCard, ModelCard, PromptCard, ExperimentCard]):
                Optional card to add to the service. If provided, arguments will
                be extracted from the card. This card must be registered in a registry.
            drift (DriftConfig | None):
                Optional drift configuration for the card. This is used to
                configure drift detection for the card in the service.


        Example:

        ```python
        from opsml import Card, ServiceCard, RegistryType

        # With arguments
        card = Card(
            alias="my_alias",
            registry_type=RegistryType.Model,
            space="my_space",
            name="my_name",
            version="1.0.0",
        )

        # With card uid
        card = Card(
            alias="my_alias",
            registry_type=RegistryType.Model,
            uid="my_uid",
        )

        # With registered card
        card = Card(
            alias="my_alias",
            card=model_card,  # ModelCard object
        )
        ```

        """

    @property
    def alias(self) -> str:
        """Alias used to reference this card within the service."""

    @property
    def space(self) -> str:
        """Space this card belongs to."""

    @property
    def name(self) -> str:
        """Name of the card."""

    @property
    def version(self) -> Optional[str]:
        """Version specifier for the card."""

    @property
    def registry_type(self) -> RegistryType:
        """Registry type of the card."""

    @property
    def drift(self) -> Optional[DriftConfig]:
        """Drift detection configuration if enabled."""

    @property
    def uid(self) -> Optional[str]:
        """Unique identifier of the card."""

class McpCapability:
    """
    Enum representing Model Context Protocol capabilities.

    Attributes:
        Resources: Resource access capability
        Tools: Tool invocation capability
        Prompts: Prompt template capability
    """

    Resources: "McpCapability"
    Tools: "McpCapability"
    Prompts: "McpCapability"

class McpTransport:
    """
    Enum representing Model Context Protocol transport types.

    Attributes:
        Http: HTTP-based transport
        Stdio: Standard I/O transport
    """

    Http: "McpTransport"
    Stdio: "McpTransport"

class McpConfig:
    def __init__(
        self,
        capabilities: List[McpCapability],
        transport: McpTransport,
    ):
        """Initialize MCP service configuration.

        Required when service type is 'Mcp'.

        Args:
            capabilities: List of MCP capabilities to enable (resources, tools, prompts)
            transport: Transport protocol to use (http or stdio)

        Raises:
            ValueError: If capabilities list is empty
        """

    @property
    def capabilities(self) -> List[McpCapability]:
        """List of enabled MCP capabilities."""

    @property
    def transport(self) -> McpTransport:
        """Transport protocol for MCP communication."""

class ServiceCard:
    """Creates a ServiceCard to hold a collection of cards."""

    def __init__(
        self,
        space: str,
        name: str,
        cards: List[Card],
        version: Optional[str] = None,
        service_type: Optional[ServiceType] = None,
        load_spec: bool = False,
    ) -> None:
        """Initialize the service card

        Args:
            space (str):
                The space of the service card
            name (str):
                The name of the service card
            cards (List[Card]):
                The cards in the service card
            version (str | None):
                The version of the service card. If not provided, the latest version
                for a given space and name will be used (e.g. {space}/{name}/v*).
            service_type (ServiceType | None):
                The type of service (Api, Mcp, Agent). If not provided, defaults to Api.
            load_spec (bool):
                Whether to load the opsmlspec.yaml file if it exists in the service card directory.
                This is useful when you have additional metadata in the opsmlspec.yaml file that you want
                to include in the service card. Defaults to False.
        """

    @property
    def space(self) -> str:
        """Return the space of the service card"""

    @property
    def name(self) -> str:
        """Return the name of the service card"""

    @property
    def version(self) -> str:
        """Return the version of the service card"""

    @property
    def uid(self) -> str:
        """Return the uid of the service card"""

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp"""

    @property
    def cards(self) -> List["CardT"]:
        """Return the cards in the service card"""

    @property
    def opsml_version(self) -> str:
        """Return the opsml version"""

    def save(self, path: Path) -> None:
        """Save the service card to a directory

        Args:
            path (Path):
                Path to save the service card.
        """

    def model_validate_json(self, json_string: str) -> "ServiceCard":
        """Load service card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def load(
        self,
        load_kwargs: Optional[Dict[str, ModelLoadKwargs | DataLoadKwargs]] = None,
    ) -> None:
        """Call the load method on each Card that requires additional loading.
        This applies to ModelCards and DataCards. PromptCards and ExperimentCards
        do not require additional loading and are loaded automatically when loading
        the ServiceCard from the registry.

        Args:
            load_kwargs (Dict[str, ModelLoadKwargs | DataLoadKwargs]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias":  DataLoadKwargs | ModelLoadKwargs
                }
        """

    @staticmethod
    def from_path(
        path: Optional[Path] = None,
        load_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "ServiceCard":
        """Loads a service card and its associated cards from a filesystem path.

        Args:
            path (Path):
                Path to load the service card from. Defaults to "service".
            load_kwargs (Dict[str, Dict[str, Any]]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias": {
                        "interface": interface_object,
                        "load_kwargs": DataLoadKwargs | ModelLoadKwargs
                    }
                }

        Returns:
            ServiceCard: The loaded service card with all cards instantiated.

        Raises:
            PyError: If service card JSON cannot be read
            PyError: If cards cannot be loaded
            PyError: If invalid kwargs are provided

        Example:
            ```python
            # Load with custom kwargs for model loading
            load_kwargs = {
                "model_card": {
                    "load_kwargs": ModelLoadKwargs(load_onnx=True)
                }
            }
            service = ServiceCard.from_path(load_kwargs=load_kwargs)
            ```
        """

    def __getitem__(self, alias: str) -> Union[DataCard, ModelCard, PromptCard, ExperimentCard]:
        """Get a card from the service card by alias

        Args:
            alias (str):
                The alias of the card to get

        Returns:
            Card:
                The card with the given alias
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with each card in the service card. This method
        will always overwrite existing artifacts.

        If the path is not provided, the artifacts will be saved to a directory.

        ```
        service/
        |-- {name}-{version}/
            |-- alias1/
            |-- alias2/
            |-- alias3/
        `-- ...
        ```

        Args:
            path (Path):
                Top-level Path to download the artifacts to. If not provided, the artifacts will be saved
                to a directory using the ServiceCard name.
        """

    @property
    def metadata(self) -> Optional["ServiceMetadata"]:
        """Return the metadata of the service card. This includes the metadata of each card in the service card as well as
        additional metadata about the service card itself (e.g. opsml version, service type, etc.)
        """

    @property
    def deploy(self) -> Optional[List[DeploymentConfig]]:
        """Return the deployment configuration for the service card if it exists"""

    @property
    def service_config(self) -> Optional[ServiceConfig]:
        """Return the service configuration for the service card if it exists"""

# Define a TypeVar that can only be one of our card types
CardT = TypeVar(
    "CardT",
    DataCard,
    ModelCard,
    PromptCard,
    ExperimentCard,
    ServiceCard,
)

class CardRegistry(Generic[CardT]):
    def __init__(self, registry_type: Union[RegistryType, str]) -> None:
        """Interface for connecting to any of the Card registries

        Args:
            registry_type (RegistryType | str):
                The type of registry to connect to. Can be a `RegistryType` or a string

        Returns:
            Instantiated connection to specific Card registry


        Example:
        ```python
            data_registry = CardRegistry(RegistryType.Data)
            data_registry.list_cards()

            or
            data_registry = CardRegistry("data")
            data_registry.list_cards()
        ```
        """

    @property
    def registry_type(self) -> RegistryType:
        """Returns the type of registry"""

    @property
    def table_name(self) -> str:
        """Returns the table name for the registry"""

    @property
    def mode(self) -> RegistryMode:
        """Returns the mode of the registry"""

    def list_cards(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by_timestamp: Optional[bool] = False,
        limit: int = 25,
    ) -> CardList:
        """Retrieves records from registry

        Args:
            uid (str):
                Unique identifier for Card. If present, the uid takes precedence
            space (str):
                Optional space associated with card
            name (str):
                Optional name of card
            version (str):
                Optional version number of existing data. If not specified, the
                most recent version will be used
            tags (List[str]):
                Optional list of tags to search for
            max_date (str):
                Optional max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01").
                Must be in the format "YYYY-MM-DD"
            sort_by_timestamp:
                If True, sorts by timestamp descending
            limit (int):
                Places a limit on result list. Results are sorted by SemVer.
                Defaults to 25.

        Returns:
            List of Cards
        """

    def register_card(
        self,
        card: CardT,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs | DataSaveKwargs | PromptSaveKwargs] = None,
    ) -> None:
        """Register a Card

        Args:
            card (ArtifactCard):
                Card to register. Can be a DataCard, ModelCard,
                experimentcard.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (SaveKwargs):
                Optional SaveKwargs to pass to the Card interface (If using DataCards
                and ModelCards).

        """

    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[LoadInterfaceType] = None,
    ) -> CardT:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.
            interface (LoadInterfaceType, optional):
                Interface to load the card with. Required for cards registered with custom interfaces.
                The expected interface type depends on the registry:

                - DataCard registry: DataInterface
                - ModelCard registry: ModelInterface
                - ExperimentCard registry: Not used
                - PromptCard registry: Not used
                - ServiceCard registry: Dict[str, Union[DataInterface, ModelInterface]]
                  Keys should be card aliases within the service.

        Returns:
            Union[DataCard, ModelCard, PromptCard, ExperimentCard, ServiceCard]:
                The loaded card instance from the registry.
        """

    def update_card(
        self,
        card: CardT,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ArtifactCard):
                Card to update. Can be a DataCard, ModelCard,
                experimentcard.
        """

    def delete_card(
        self,
        card: CardT,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ArtifactCard):
                Card to delete. Can be a DataCard, ModelCard,
                experimentcard.
        """

class ModelCardRegistry(CardRegistry):
    def register_card(
        self,
        card: ModelCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs] = None,  # type: ignore
    ) -> None:
        """Register a Card

        Args:
            card (ModelCard):
                ModelCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (ModelSaveKwargs):
                Optional SaveKwargs to pass to the Card interface

        """

    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[ModelInterface] = None,  # type: ignore
    ) -> ModelCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.
            interface (ModelInterface, optional):
                Interface to load the card with. Required for cards registered with custom interfaces.

        Returns:
            ModelCard
        """

    def update_card(
        self,
        card: ModelCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ModelCard):
                Card to update
        """

    def delete_card(
        self,
        card: ModelCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ModelCard):
                Card to delete. Can be a DataCard, ModelCard,
                experimentcard.
        """

class DataCardRegistry(CardRegistry):
    def register_card(
        self,
        card: DataCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[DataSaveKwargs] = None,  # type: ignore
    ) -> None:
        """Register a Card

        Args:
            card (DataCard):
                DataCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (DataSaveKwargs):
                Optional SaveKwargs to pass to the Card interface

        """

    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[DataInterface] = None,  # type: ignore
    ) -> DataCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.
            interface (DataInterface, optional):
                Interface to load the card with. Required for cards registered with custom interfaces.

        Returns:
            DataCard
        """

    def update_card(
        self,
        card: DataCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (DataCard):
                Card to update
        """

    def delete_card(
        self,
        card: DataCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (DataCard):
                Card to delete
        """

class ExperimentCardRegistry(CardRegistry):
    def register_card(  # type: ignore
        self,
        card: ExperimentCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
    ) -> None:
        """Register a Card

        Args:
            card (ExperimentCard):
                ExperimentCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.

        """

    def load_card(  # type: ignore
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> ExperimentCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.

        Returns:
            ExperimentCard
        """

    def update_card(
        self,
        card: ExperimentCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ExperimentCard):
                Card to update.
        """

    def delete_card(
        self,
        card: ExperimentCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ExperimentCard):
                Card to delete
        """

class PromptCardRegistry(CardRegistry):
    def register_card(  # type: ignore
        self,
        card: PromptCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[PromptSaveKwargs] = None,
    ) -> None:
        """Register a Card

        Args:
            card (PromptCard):
                PromptCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (PromptSaveKwargs):
                Optional SaveKwargs to pass to the Card interface

        """

    def load_card(  # type: ignore
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> PromptCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.

        Returns:
            PromptCard
        """

    def update_card(
        self,
        card: PromptCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (PromptCard):
                Card to update
        """

    def delete_card(
        self,
        card: PromptCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (PromptCard):
                Card to delete
        """

class ServiceCardRegistry(CardRegistry):
    def register_card(  # type: ignore
        self,
        card: ServiceCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
    ) -> None:
        """Register a Card

        Args:
            card (ServiceCard):
                ServiceCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.

        """

    def load_card(  # type: ignore
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> ServiceCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.

        Returns:
            ServiceCard
        """

    def update_card(
        self,
        card: ServiceCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ServiceCard):
                Card to update
        """

    def delete_card(
        self,
        card: ServiceCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ServiceCard):
                Card to delete
        """

class CardRegistries:
    def __init__(self) -> None: ...
    @property
    def data(self) -> DataCardRegistry: ...
    @property
    def model(self) -> ModelCardRegistry: ...
    @property
    def experiment(self) -> ExperimentCardRegistry: ...
    @property
    def audit(self) -> CardRegistry: ...
    @property
    def prompt(self) -> PromptCardRegistry: ...
    @property
    def service(self) -> ServiceCardRegistry: ...

def download_service(
    write_dir: Path,
    space: Optional[str] = None,
    name: Optional[str] = None,
    version: Optional[str] = None,
    uid: Optional[str] = None,
) -> None:
    """Download a service from the registry.

    Args:
        space (str):
            Space associated with the service.
        name (str):
            Name of the service.
        version (str):
            Version number of the service.
        uid (str):
            Unique identifier for the service.
        write_dir (str):
            Directory to write the downloaded service to.
    """

class ExperimentMetric:
    def __init__(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
    ) -> None:
        """
        Initialize a Metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    @property
    def name(self) -> str:
        """
        Name of the metric
        """

    @property
    def value(self) -> float:
        """
        Value of the metric
        """

    @property
    def step(self) -> Optional[int]:
        """
        Step of the metric
        """

    @property
    def timestamp(self) -> Optional[int]:
        """
        Timestamp of the metric
        """

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        """
        Created at of the metric
        """

class ExperimentMetrics:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Metric: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class Parameter:
    def __init__(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Initialize a Parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    @property
    def name(self) -> str:
        """
        Name of the parameter
        """

    @property
    def value(self) -> Union[int, float, str]:
        """
        Value of the parameter
        """

class Parameters:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Parameter: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class Experiment:
    def start_experiment(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[Path] = None,
        log_hardware: bool = False,
        experiment_uid: Optional[str] = None,
    ) -> "Experiment":
        """
        Start an Experiment

        Args:
            space (str | None):
                space to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            code_dir (Path | None):
                Directory to log code from
            log_hardware (bool):
                Whether to log hardware information or not
            experiment_uid (str | None):
                Experiment UID. If provided, the experiment will be loaded from the server.

        Returns:
            Experiment
        """

    def __enter__(self) -> "Experiment":
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def log_metric(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
    ) -> None:
        """
        Log a metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    def log_metrics(self, metrics: list[ExperimentMetric]) -> None:
        """
        Log multiple metrics

        Args:
            metrics (list[Metric]):
                List of metrics to log
        """

    def log_eval_metrics(self, metrics: "EvalMetrics") -> None:
        """
        Log evaluation metrics

        Args:
            metrics (EvalMetrics):
                Evaluation metrics to log
        """

    def log_parameter(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Log a parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    def log_parameters(self, parameters: list[Parameter] | Dict[str, Union[int, float, str]]) -> None:
        """
        Log multiple parameters

        Args:
            parameters (list[Parameter] | Dict[str, Union[int, float, str]]):
                Parameters to log
        """

    def log_artifact(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log an artifact

        Args:
            lpath (Path):
                The local path where the artifact has been saved to
            rpath (Optional[str]):
                The path to associate with the artifact in the experiment artifact directory
                {experiment_path}/artifacts. If not provided, defaults to
                {experiment}/artifacts/{filename}
        """

    def log_figure_from_path(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log a figure

        Args:
            lpath (Path):
                The local path where the figure has been saved to. Must be an image type
                (e.g. jpeg, tiff, png, etc.)
            rpath (Optional[str]):
                The path to associate with the figure in the experiment artifact directory
                {experiment_path}/artifacts/figures. If not provided, defaults to
                {experiment}/artifacts/figures/{filename}

        """

    def log_figure(self, name: str, figure: Any, kwargs: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a figure. This method will log a matplotlib Figure object to the experiment artifacts.

        Args:
            name (str):
                Name of the figure including its file extension
            figure (Any):
                Figure to log
            kwargs (Optional[Dict[str, Any]]):
                Additional keyword arguments
        """

    def log_artifacts(
        self,
        paths: Path,
    ) -> None:
        """
        Log multiple artifacts

        Args:
            paths (Path):
                Paths to a directory containing artifacts.
                All files in the directory will be logged.
        """

    @property
    def card(self) -> "ExperimentCard":
        """
        ExperimentCard associated with the Experiment
        """

    def register_card(
        self,
        card: Union[DataCard, ModelCard, PromptCard],
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs | DataSaveKwargs] = None,
    ) -> None:
        """Register a Card as part of an experiment

        Args:
            card (DataCard | ModelCard):
                Card to register. Can be a DataCard or a ModelCard
            version_type (VersionType):
                How to increment the version SemVer. Default is VersionType.Minor.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (SaveKwargs):
                Optional SaveKwargs to pass to the Card interface (If using DataCards
                and ModelCards).

        """

def start_experiment(
    space: Optional[str] = None,
    name: Optional[str] = None,
    code_dir: Optional[Path] = None,
    log_hardware: bool = False,
    experiment_uid: Optional[str] = None,
) -> Experiment:
    """
    Start an Experiment

    Args:
        space (str | None):
            space to associate with `ExperimentCard`
        name (str | None):
            Name to associate with `ExperimentCard`
        code_dir (Path | None):
            Directory to log code from
        log_hardware (bool):
            Whether to log hardware information or not
        experiment_uid (str | None):
            Experiment UID. If provided, the experiment will be loaded from the server.

    Returns:
        Experiment
    """

class EvalMetrics:
    """
    Map of metrics used that can be used to evaluate a model.
    The metrics are also used when comparing a model with other models
    """

    def __init__(self, metrics: Dict[str, float]) -> None:
        """
        Initialize EvalMetrics

        Args:
            metrics (Dict[str, float]):
                Dictionary of metrics containing the name of the metric as the key and its value as the value.
        """

    def __getitem__(self, key: str) -> float:
        """Get the value of a metric by name. A RuntimeError will be raised if the metric does not exist."""

def get_experiment_metrics(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Metrics:
    """
    Get metrics of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the metrics to get. If None, all metrics will be returned.

    Returns:
        Metrics
    """

def get_experiment_parameters(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Parameters:
    """
    Get parameters of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the parameters to get. If None, all parameters will be returned.

    Returns:
        Parameters
    """

def download_artifact(
    experiment_uid: str,
    path: Path,
    lpath: Optional[Path] = None,
) -> None:
    """
    Download an artifact from an experiment
    Args:
        experiment_uid (str):
            UID of the experiment
        path (Path):
            Path of the artifact to download
        lpath (Path | None):
            Local path to download the artifact to. If None, the artifact will be downloaded to the current working directory.
    """

__all__ = [
    "ServiceType",
    "CardRecord",
    "CardList",
    "DataCard",
    "DataCardMetadata",
    "RegistryType",
    "RegistryMode",
    "ModelCard",
    "ModelCardMetadata",
    "ComputeEnvironment",
    "ExperimentCard",
    "PromptCard",
    "Card",
    "ServiceCard",
    "McpCapability",
    "McpTransport",
    "McpConfig",
    "CardRegistry",
    "CardRegistries",
    "download_service",
    "ExperimentMetric",
    "ExperimentMetrics",
    "Parameter",
    "Parameters",
    "Experiment",
    "start_experiment",
    "EvalMetrics",
    "get_experiment_metrics",
    "get_experiment_parameters",
    "download_artifact",
]
