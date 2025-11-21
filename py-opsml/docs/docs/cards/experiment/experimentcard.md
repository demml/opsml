
`Experimentcards` are used to store metrics and artifacts related to `DataCards` and `ModelCards`. While a experimentcard can be used as a object itself, it's best to use it as a context manager.

### Creating an Experiment
Experiments are unique context-managed executions that record all created cards and their associated metrics, params, and artifacts to a single card called a `Experimentcard`.

If you're familiar with how other libraries do it, then nothing is really going to seem new. Refer to [usage](/opsml/docs/cards/experiment/usage/) for more detailed information.

### Traditional Example

```python
from opsml import start_experiment, SklearnModel, ModelCard # (1)
from opsml.helpers.data import create_fake_data

with start_experiment(space="opsml", log_hardware=True) as exp: # (2)

    X, y = create_fake_data(n_samples=1200)
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X.to_numpy(), y.to_numpy().ravel())

    random_forest_classifier = SklearnModel(
        model=reg,
        sample_data=X_train,
        task_type=TaskType.Classification,
        preprocessor=StandardScaler(),
    )

    modelcard = ModelCard(
            interface=random_forest_classifier,
            tags=["foo:bar", "baz:qux"],
        )

    exp.register_card(modelcard) # (3)
    exp.log_metric("accuracy", 0.95) # (4)
    exp.log_parameter("epochs", 10) # (5)
```

1. The recommended way to start an experiment is to use the `start_experiment` function. This will create a new experiment card and return it as a context manager which you can use to log metrics, parameters, artifacts and cards.
2. The are a few arguments that can be passed to the `start_experiment` function (see definition). In this case we are only supplying the `space` argument and we are opting in to record hardware metrics.
3. The `register_card` method is used to register a card to the experiment. This will automatically register the card in it's associated registry as well as associate it with the experiment card.
4. The `log_metric` method is used to log a metric to the experiment card. This will automatically register the metric in it's associated registry as well as associate it with the experiment card. Metrics are logged in real-time.
5. The `log_parameter` method is used to log a parameter to the experiment card. This will automatically register the parameter in it's associated registry as well as associate it with the experiment card. Parameters are logged in real-time.

### GenAI Example

```python
from opsml import start_experiment, PromptCard, Prompt

with start_experiment(space="opsml", log_hardware=True) as exp:

    prompt = Prompt(
        model="gpt-4o",
        message="what is 2 + 2?",
        provider="openai",
        system_instruction="You are a helpful assistant.",
    )

    # ... your code here to test and validate the prompt
    # exp.log_metric(...)
    # exp.log_parameter(...)
    # exp.log_artifact(...)

    prompt_card = PromptCard(prompt)
    exp.register_card(prompt_card)
```

You can now log into the opsml server and see your recent experiment and associated metadata

### Definitions

???success "start_experiment"
    ```python
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
                Directory to log code from. If None, only the current python file will be logged.
            log_hardware (bool):
                Whether to log hardware information or not
            experiment_uid (str | None):
                Experiment UID. If provided, the experiment will be loaded from the server.

        Returns:
            Experiment
        """
    ```

???success "Experiment"
    ```python
    class Experiment:
        """Core class returned by the start_experiment function"""
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
            created_at: Optional[datetime] = None,
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

        def log_metrics(self, metrics: list[Metric]) -> None:
            """
            Log multiple metrics

            Args:
                metrics (list[Metric]):
                    List of metrics to log
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

        def log_parameters(self, parameters: list[Parameter]) -> None:
            """
            Log multiple parameters

            Args:
                parameters (list[Parameter]):
                    List of parameters to log
            """

        def log_artifact(
            self,
            path: Path,
        ) -> None:
            """
            Log an artifact

            Args:
                path (Path):
                    Path to the artifact file. Path must be a file.
                    If logging multiple artifacts, use `log_artifacts` instead.
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
    ```

### Accessing the ExperimentCard

You can access the experiment card and it's associated metrics, parameters and artifacts by loading the card from the registry

```python

from opsml import CardRegistry, RegistryType, get_experiment_metrics, get_experiment_parameters

registry = CardRegistry(RegistryType.Experiment)

card = registry.load_card(uid="{{experiment uid}}")

# you can now access the card and it's associated metadata
card.list_artifacts()
card.download_artifacts()
card.get_metrics()
card.get_parameters()


# if you want to access the metrics and parameters directly, you can use the following functions
metrics = get_experiment_metrics(card.uid)
parameters = get_experiment_parameters(card.uid)
```

???success "ExperimentCard"
    ```python
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
    ```