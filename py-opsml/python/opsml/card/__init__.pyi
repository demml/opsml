# pylint: disable=dangerous-default-value
# type: ignore
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    TypeAlias,
    TypeVar,
    Union,
    overload,
)

from ..data import DataInterface, DataLoadKwargs, DataSaveKwargs, DataType
from ..experiment import EvalMetrics, Metrics, Parameters
from ..llm import Prompt, Workflow
from ..model import (
    DriftProfileMap,
    FeatureSchema,
    ModelInterface,
    ModelLoadKwargs,
    ModelSaveKwargs,
    OnnxSession,
)
from ..scouter.drift import LLMDriftConfig, LLMDriftProfile, LLMMetric
from ..types import VersionType

CardInterfaceType: TypeAlias = Union[DataInterface, ModelInterface]
ServiceCardInterfaceType: TypeAlias = Dict[str, Union[DataInterface, ModelInterface]]
LoadInterfaceType: TypeAlias = Union[ServiceCardInterfaceType, ServiceCardInterfaceType]

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Experiment: "RegistryType"
    Audit: "RegistryType"
    Prompt: "RegistryType"
    Deck: "RegistryType"

class RegistryMode:
    Client: "RegistryMode"
    Server: "RegistryMode"

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
    def created_at(self) -> datetime:
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
    def metadata(self) -> DataCardMetadata:  # pylint: disable=used-before-assignment
        """Return the metadata of the data card"""

    @property
    def registry_type(self) -> RegistryType:
        """Return the card type of the data card"""

    @property
    def data_type(self) -> DataType:
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

class DataCardMetadata:
    @property
    def schema(self) -> FeatureSchema:
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
    def created_at(self) -> datetime:
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
    def drift_profile(self) -> DriftProfileMap:
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
    ) -> Parameters:
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
    def eval_metrics(self) -> EvalMetrics:
        """Returns the eval metrics of the `experimentcard`"""

    @eval_metrics.setter
    def eval_metrics(self, metrics: EvalMetrics) -> None:
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
    def created_at(self) -> datetime:
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
        drift_profile: Optional[Dict[str, LLMDriftProfile]] = None,
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
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile. Currently supports LLM drift profiles.
        Example:
        ```python
        from opsml import Prompt, PromptCard, CardRegistry, RegistryType

        # create prompt
        prompt = Prompt(
            model="openai:gpt-4o",
            message=[
                "My prompt $1 is $2",
                "My prompt $3 is $4",
            ],
            system_instruction="system_prompt",
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
    def create_drift_profile(
        self,
        alias: str,
        config: LLMDriftConfig,
        metrics: List[LLMMetric],
        workflow: Optional[Workflow] = None,
    ) -> None:
        """Create an LLMDriftProfile for LLM evaluation and drift detection.

        LLM evaluations are run asynchronously on the scouter server.

        Logic flow:
            1. If only metrics are provided, a workflow will be created automatically
               from the metrics. In this case a prompt is required for each metric.
            2. If a workflow is provided, it will be parsed and validated for compatibility:
               - A list of metrics to evaluate workflow output must be provided
               - Metric names must correspond to the final task names in the workflow

        Baseline metrics and thresholds will be extracted from the LLMMetric objects.

        Args:
            config (LLMDriftConfig):
                The configuration for the LLM drift profile containing space, name,
                version, and alert settings.
            metrics (list[LLMMetric]):
                A list of LLMMetric objects representing the metrics to be monitored.
                Each metric defines evaluation criteria and alert thresholds.
            workflow (Optional[Workflow]):
                Optional custom workflow for advanced evaluation scenarios. If provided,
                the workflow will be validated to ensure proper parameter and response
                type configuration.

        Returns:
            LLMDriftProfile: Configured profile ready for LLM drift monitoring.

        Raises:
            ProfileError: If workflow validation fails, metrics are empty when no
                workflow is provided, or if workflow tasks don't match metric names.

        Examples:
            Basic usage with metrics only:

            >>> config = LLMDriftConfig("my_space", "my_model", "1.0")
            >>> metrics = [
            ...     LLMMetric("accuracy", 0.95, AlertThreshold.Above, 0.1, prompt),
            ...     LLMMetric("relevance", 0.85, AlertThreshold.Below, 0.2, prompt2)
            ... ]
            >>> profile = Drifter().create_llm_drift_profile(config, metrics)

            Advanced usage with custom workflow:

            >>> workflow = create_custom_workflow()  # Your custom workflow
            >>> metrics = [LLMMetric("final_task", 0.9, AlertThreshold.Above)]
            >>> profile = Drifter().create_llm_drift_profile(config, metrics, workflow)

        Note:
            - When using custom workflows, ensure final tasks have Score response types
            - Initial workflow tasks must include "input" and/or "response" parameters
            - All metric names must match corresponding workflow task names
        """

    @property
    def drift_profile(self) -> DriftProfileMap:
        """Return the drift profile map from the model interface.

        Returns:
            DriftProfileMap
        """

    @drift_profile.setter
    def drift_profile(self, drift_profile: DriftProfileMap) -> None:
        """Set the drift profile map for the prompt card.

        Args:
            drift_profile (DriftProfileMap):
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
        card: Optional[CardType] = None,
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

class ServiceCard:
    """Creates a ServiceCard to hold a collection of cards."""

    def __init__(
        self,
        space: str,
        name: str,
        cards: List[Card],
        version: Optional[str],
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
    def created_at(self) -> datetime:
        """Return the created at timestamp"""

    @property
    def cards(self) -> List[CardType]:
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

    def __getitem__(self, alias: str) -> CardType:
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

# Define a TypeVar that can only be one of our card types
CardType = TypeVar(  # pylint: disable=invalid-name
    "CardType",
    DataCard,
    ModelCard,
    PromptCard,
    ExperimentCard,
    ServiceCard,
)

class CardRegistry(Generic[CardType]):
    @overload
    def __init__(self, registry_type: Literal[RegistryType.Data]) -> "CardRegistry[DataCard]": ...
    @overload
    def __init__(self, registry_type: Literal[RegistryType.Model]) -> "CardRegistry[ModelCard]": ...
    @overload
    def __init__(self, registry_type: Literal[RegistryType.Prompt]) -> "CardRegistry[PromptCard]": ...
    @overload
    def __init__(self, registry_type: Literal[RegistryType.Experiment]) -> "CardRegistry[ExperimentCard]": ...
    @overload
    def __init__(self, registry_type: Literal[RegistryType.Service]) -> "CardRegistry[ServiceCard]": ...
    @overload
    def __init__(self, registry_type: Literal[RegistryType.Audit]) -> "CardRegistry[Any]": ...

    # String literal overloads
    @overload
    def __init__(self, registry_type: Literal["data"]) -> "CardRegistry[DataCard]": ...
    @overload
    def __init__(self, registry_type: Literal["model"]) -> "CardRegistry[ModelCard]": ...
    @overload
    def __init__(self, registry_type: Literal["prompt"]) -> "CardRegistry[PromptCard]": ...
    @overload
    def __init__(self, registry_type: Literal["experiment"]) -> "CardRegistry[ExperimentCard]": ...
    @overload
    def __init__(self, registry_type: Literal["service"]) -> "CardRegistry[ServiceCard]": ...
    @overload
    def __init__(self, registry_type: Literal["audit"]) -> "CardRegistry[Any]": ...
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
        card: CardType,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs=Optional[ModelSaveKwargs | DataSaveKwargs],
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

    @overload
    def load_card(
        self: "CardRegistry[DataCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[DataInterface] = None,
    ) -> DataCard: ...
    @overload
    def load_card(
        self: "CardRegistry[ServiceCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface=Optional[ServiceCardInterfaceType],
    ) -> ServiceCard: ...
    @overload
    def load_card(
        self: "CardRegistry[ModelCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[ModelInterface] = None,
    ) -> ModelCard: ...
    @overload
    def load_card(
        self: "CardRegistry[PromptCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: None = None,
    ) -> PromptCard: ...
    @overload
    def load_card(
        self: "CardRegistry[ExperimentCard]",
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: None = None,
    ) -> ExperimentCard: ...
    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[LoadInterfaceType] = None,
    ) -> Union[DataCard, ModelCard, PromptCard, ExperimentCard, ServiceCard]:
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
        card: CardType,
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
        card: CardType,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ArtifactCard):
                Card to delete. Can be a DataCard, ModelCard,
                experimentcard.
        """

class CardRegistries:
    def __init__(self) -> None: ...
    @property
    def data(self) -> CardRegistry[DataCard]: ...
    @property
    def model(self) -> CardRegistry[ModelCard]: ...
    @property
    def experiment(self) -> CardRegistry[ExperimentCard]: ...
    @property
    def audit(self) -> CardRegistry[Any]: ...
    @property
    def prompt(self) -> CardRegistry[PromptCard]: ...
    @property
    def service(self) -> CardRegistry[ServiceCard]: ...

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
