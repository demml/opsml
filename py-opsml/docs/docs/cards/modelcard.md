
ModelCards help you store, version, and track model objects.

## Features
- **shareable**: All cards including ModelCards are shareable and searchable.
- **auto-schema**: Auto-infer data schema.
- **auto-metadata**: Extract model-specific metadata to associate with the card.
- **versioning**: Semver for your model.
- **auto-onnx**: Optional automatic conversion of trained model into onnx model format.

## Create a Card

```python
from opsml.helpers.data import create_fake_data
from typing import Tuple, cast
import pandas as pd
from opsml import (  # type: ignore
    SklearnModel,
    PandasData,
    CardRegistries,
    TaskType,
    DataCard,
    ModelCard,
)
from opsml.data import DataSplit, StartStopSplit
from sklearn import ensemble  # type: ignore


# start registries
reg = CardRegistries()

# create data
X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))
X["target"] = y

# create data splits to store with the model (optional)
data_splits = [
    DataSplit(  # (1)
        label="train",
        start_stop_split=StartStopSplit(
            start=0,
            stop=1000,
        ),
    ),
    DataSplit(
        label="test",
        start_stop_split=StartStopSplit(
            start=1000,
            stop=1200,
        ),
    ),
]

# create DataCard
datacard = DataCard(
    interface=PandasData(
        data=X,
        data_splits=data_splits,
        dependent_vars=["target"],
    ),
    space="opsml",
    name="my_data",
    tags=["foo:bar", "baz:qux"],
)

# register DataCard
reg.data.register_card(datacard)

splits = datacard.interface.split_data()

# Create and train model
classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(
    splits["train"].x.to_numpy(),
    splits["train"].y.to_numpy().ravel(),
)

model_interface = SklearnModel( # (2)
    model=classifier,
    sample_data=X[0:10],
    task_type=TaskType.Classification,
)

model_interface.create_drift_profile(alias="drift", X)

modelcard = ModelCard( # (3)
    interface=model_interface,
    space="opsml",
    name="my_model",
    tags=["foo:bar", "baz:qux"],
    datacard_uid=datacard.uid,
)

# register model
reg.model.register_card(modelcard)
```

1. DataSplits allow you to create and store split logic with your DataInterface ensuring reproducibility
2. Here we are using the SklearnModel interface and passing in the trained model, sample data, and the task type
3. Here we are creating a ModelCard and passing in the model interface, space, name, tags, and the datacard_uid. The datacard_uid is used to link the model to the data it was trained on

### How it all works

As you can tell in the example above, `ModelCards` are created by passing in a `ModelInterface`, some required args and some optional args. The `ModelInterface` is the interface is a library-specific interface for saving and extracting metadata from the model. It also allows us to standardize how models are saved (by following the library's guidelines) and ensures reproducibility.

## Load a Card's Components

By default, `OpsML` **does not** load any of the model components (model, preprocessor, etc.) when loading a card. This is to ensure that the card is loaded as quickly as possible. If you wish to load the model components, you can do so by calling the `load` method on the `ModelCard`

```python
from opsml import CardRegistry, RegistryType

# start registries
reg = CardRegistry(RegistryType.Model)

# load model card
modelcard = reg.load_card(uid="{{model uid}}")

# load the model
modelcard.load()

# load with the onnx model as well
modelcard.load(load_kwargs=ModelLoadKwargs(load_onnx=True)) #(1)
```

1. For the majority of use cases, load() is enough. However, there are optional arguments you can pass for things like loading an onnx model.

???success "ModelCard"
    ```python
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
            registry = CardRegistry(RegistryType.Model)
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
            ...


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
    ```


## Model Interface

The `ModelInterface` is the primary interface for working with models in `Opsml`. It is designed to be subclassed and can be used to store models in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `SklearnModel`: Stores data from a sklearn model - [link](#sklearnmodel)
- `TorchModel`: Stores data from a pytorch model - [link](#torchmodel)
- `LightningModel`: Stores data from a pytorch lightning model - [link](#lightningmodel)
- `HuggingFaceModel`: Stores data from a huggingface model - [link](#huggingfacemodel)
- `TensorFlowModel`: Stores data from a tensorflow model - [link](#tensorflowmodel)
- `XGBoostModel`: Stores data from a xgboost model - [link](#xgboostmodel)
- `LightGBMModel`: Stores data from a lightgbm model - [link](#lightgbmmodel)
- `CatBoostModel`: Stores data from a catboost model - [link](#catboostmodel)
- `Custom`: Create your own model interface - [link](#custommodel)

### Shared Arguments for all Model Interfaces

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface  |
| <span class="text-alert">**sample_data**</span>  | Optional sample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

???success "ModelInterface"
    ```python
    class ModelInterface:
        def __init__(
            self,
            model: None | Any = None,
            sample_data: None | Any = None,
            task_type: None | TaskType = None,
            drift_profile: (
                None
                | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
                | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            ) = None,
        ) -> None:
            """Base class for ModelInterface

            Args:
                model:
                    Model to associate with interface.
                sample_data:
                    Sample data to use to make predictions
                task_type:
                    The type of task the model performs
                drift_profile:
                    Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
            """

        @property
        def model(self) -> None | Any:
            """Returns the model"""

        @model.setter
        def model(self, model: Any) -> None:
            """Sets the model"""

        @property
        def sample_data(self) -> None | Any:
            """Returns the sample data"""

        @sample_data.setter
        def sample_data(self, sample_data: Any) -> None:
            """Sets the sample data"""

        @property
        def data_type(self) -> DataType:
            """Returns the task type"""

        @property
        def task_type(self) -> TaskType:
            """Returns the task type"""

        @property
        def schema(self) -> FeatureSchema:
            """Returns the feature schema"""

        @property
        def model_type(self) -> ModelType:
            """Returns the model type"""

        @property
        def interface_type(self) -> ModelInterfaceType:
            """Returns the model type"""

        @property
        def drift_profile(
            self,
        ) -> List[Any]:
            """Returns the drift profile"""

        @drift_profile.setter
        def drift_profile(
            self,
            profile: List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile],
        ) -> None:
            """Sets the drift profile"""

        @property
        def onnx_session(self) -> None | OnnxSession:
            """Returns the onnx session if it exists"""

        @onnx_session.setter
        def onnx_session(self, session: None | OnnxSession) -> None:
            """Sets the onnx session


            Args:
                session:
                    Onnx session
            """

        @overload
        def create_drift_profile(
            self,
            alias: str,
            data: CustomMetric | List[CustomMetric],
            config: CustomMetricDriftConfig,
            data_type: Optional[DataType] = None,
        ) -> CustomDriftProfile: ...
        @overload
        def create_drift_profile(
            self,
            alias: str,
            data: Any,
            config: SpcDriftConfig,
            data_type: Optional[DataType] = None,
        ) -> SpcDriftProfile: ...
        @overload
        def create_drift_profile(
            self,
            alias: str,
            data: Any,
            config: PsiDriftConfig,
            data_type: Optional[DataType] = None,
        ) -> PsiDriftProfile: ...
        @overload
        def create_drift_profile(
            self,
            alias: str,
            data: Any,
            data_type: Optional[DataType] = None,
        ) -> SpcDriftProfile: ...
        def create_drift_profile(  # type: ignore
            self,
            alias: str,
            data: Any,
            config: None | SpcDriftConfig | PsiDriftConfig | CustomMetricDriftConfig = None,
            data_type: None | DataType = None,
        ) -> Any:
            """Create a drift profile and append it to the drift profile list

            Args:
                alias:
                    Alias to use for the drift profile. This is used to identify the drift profile in the UI and in the model card.
                data:
                    Data to use to create the drift profile. Can be a pandas dataframe,
                    polars dataframe, pyarrow table or numpy array.
                config:
                    Drift config to use. If None, defaults to SpcDriftConfig.
                data_type:
                    Data type to use. If None, data_type will be inferred from the data.

            Returns:
                Drift profile SPcDriftProfile, PsiDriftProfile or CustomDriftProfile
            """

        def save(
            self,
            path: Path,
            save_kwargs: None | ModelSaveKwargs = None,
        ) -> ModelInterfaceMetadata:
            """Save the model interface

            Args:
                path (Path):
                    Path to save the model
                save_kwargs (ModelSaveKwargs):
                    Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                    that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                    the underlying library.

                    - model: Kwargs that will be passed to save_model. See save_model for more details.
                    - preprocessor: Kwargs that will be passed to save_preprocessor
                    - onnx: Kwargs that will be passed to save_onnx_model. See convert_onnx_model for more details
            """

        def load(
            self,
            path: Path,
            metadata: ModelInterfaceSaveMetadata,
            load_kwargs: None | ModelLoadKwargs = None,
        ) -> None:
            """Load ModelInterface components

            Args:
                path (Path):
                    Path to load the model
                metadata (ModelInterfaceSaveMetadata):
                    Metadata to use to load the model
                load_kwargs (ModelLoadKwargs):
                    Optional load kwargs to pass to the different load methods
            """

        @staticmethod
        def from_metadata(metadata: ModelInterfaceMetadata) -> "ModelInterface":
            """Create a ModelInterface from metadata

            Args:
                metadata:
                    Model interface metadata

            Returns:
                Model interface
            """
    ```

### Save Method

All ModelInterfaces have a default save method that will save the model and any interface-specific addons. You typically will not have to call this method since it will be called by the specific registry. However, when registering a card, if your model requires specific kwargs such as any onnx, model or preprocessor kwargs, you can pass them in via an optional `ModelSaveKwargs` object.

```python
# ... imports

model_registry = CardRegistry(RegistryType.Model)

reg = XGBRegressor(n_estimators=3, max_depth=3)
reg.fit(X, y)

model_registry.register_card(
    card=ModelCard(
        interface=SklearnModel(model=reg),
        space="opsml",
        name="my_model",
    ),
    # special onnx kwargs to pass to model_interface save method
    save_kwargs=ModelSaveKwargs(onnx={"target_opset": {"ai.onnx.ml": 3, "": 9}}),
)
```

???success "ModelSaveKwargs"
    ```python
    class ModelSaveKwargs:
        def __init__(
            self,
            onnx: Optional[Dict | HuggingFaceOnnxArgs] = None,
            model: Optional[Dict] = None,
            preprocessor: Optional[Dict] = None,
            save_onnx: bool = False,
        ) -> None:
            """Optional arguments to pass to save_model

            Args:
                onnx (Dict or HuggingFaceOnnxArgs):
                    Optional onnx arguments to use when saving model to onnx format
                model (Dict):
                    Optional model arguments to use when saving
                preprocessor (Dict):
                    Optional preprocessor arguments to use when saving
                save_onnx (bool):
                    Whether to save the onnx model. Defaults to false. This is independent of the
                    onnx argument since it's possible to convert a model to onnx without additional kwargs.
                    If onnx args are provided, this will be set to true.
            """

        def __str__(self): ...
        def model_dump_json(self) -> str: ...
        @staticmethod
        def model_validate_json(json_string: str) -> "ModelSaveKwargs": ...
    ```

### Load Method

All ModelInterfaces have a default load method that will load the model and any interface-specific addons. You typically will not have to call this method since it will be called by the specific registry (`load`). However, when loading a card's model attributes, if your model requires specific kwargs such as any onnx, model or preprocessor kwargs, you can pass them in via an optional `ModelLoadKwargs` object.

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**onnx**</span>       | Optional onnx arguments to use when loading  |
| <span class="text-alert">**model**</span>  | Optional model arguments to use when loading time |
| <span class="text-alert">**preprocessor**</span>    | Optional preprocessor arguments to use when loading |
| <span class="text-alert">**load_onnx**</span> |  Whether to load the onnx model. Defaults to false unless onnx args are provided. If true, the onnx model will be loaded |

???success "ModelLoadKwargs"
    ```python
    class ModelLoadKwargs:
        onnx: Optional[Dict]
        model: Optional[Dict]
        preprocessor: Optional[Dict]
        load_onnx: bool

        def __init__(
            self,
            onnx: Optional[Dict] = None,
            model: Optional[Dict] = None,
            preprocessor: Optional[Dict] = None,
            load_onnx: bool = False,
        ) -> None:
            """Optional arguments to pass to load_model

            Args:
                onnx (Dict):
                    Optional onnx arguments to use when loading
                model (Dict):
                    Optional model arguments to use when loading
                preprocessor (Dict):
                    Optional preprocessor arguments to use when loading
                load_onnx (bool):
                    Whether to load the onnx model. Defaults to false unless onnx args are
                    provided. If true, the onnx model will be loaded.

            """
    ```

## SklearnModel

Interface for saving an Sklearn model

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/sklean.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be from the scikit-learn ecosystem (BaseEstimator)  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model. This preprocessor must be from the  scikit-learn ecosystem  |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

???success "SklearnModel"
    ```python
    class SklearnModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Instantiate an SklearnModel interface

        Args:
            model:
                Model to associate with interface. This model must be from the
                scikit-learn ecosystem
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""
    ```

### Nuts and Bolts

The `SklearnModel` and it's associated model and preprocessor are saved using joblib. In addition, depending upon the model type, `OpsML` will extract model-specific metadata from the provided model at the time of registration, which can be viewed in the UI and is associated with the card metadata.


## LightGBMModel

Interface for saving a LightGBM Booster model. **Note** - If using a LGBMRegressor or LGBMClassifier, you should use the SklearnModelInterface instead.


**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/lightgbm_booster.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be an lightgbm booster  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model  |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |


???success "LightGBMModel"
    ```python
    class LightGBMModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Instantiate a LightGBMModel interface

        Args:
            model:
                Model to associate with interface. This model must be a lightgbm booster.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""
    ```


### Nuts and Bolts

Booster models are saved via `save_model` which exports a `.txt` file. Preprocessors are saved via `joblib`.


## XGBoostModel

Interface for saving a XGBoostBooster model. **Note** - If using a XGBRegressor or XGBClassifier, you should use the SklearnModelInterface instead.


**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/xgb_booster.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be an xgboost booster  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

???success "XGBoostModel"
    ```python
    class XGBoostModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving XGBoost Booster models

        Args:
            model:
                Model to associate with interface. This model must be an xgboost booster.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions.
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""
    ```

### Nuts and Bolts

Booster models are saved via `save_model` which exports a `.json` file. Preprocessors are saved via `joblib`.

## HuggingFaceModel

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/hf_model.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. Model must be a `Pipeline`, `PreTrainedModel` or a `TFPreTrainedModel`  |
| <span class="text-alert">**tokenizer**</span>       | Optional tokenizer to associate with the model. Must be of type `PreTrainedTokenizerBase`  |
| <span class="text-alert">**feature_extractor**</span>      | Optional feature extractor to associate with model. Must be of type `PreTrainedFeatureExtractor` |
| <span class="text-alert">**image_processor**</span>      | Optional image processor to associate with model. Must be of type `BaseImageProcessor` |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**hf_task**</span>    | Optional HuggingFace task type of the model. Defaults to `HuggingFaceTask.Undefined` |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |


???success "HuggingFaceMode"
    ```python
    class HuggingFaceModel(ModelInterface):
        def __init__(
            self,
            model: Optional[Any] = None,
            tokenizer: Optional[Any] = None,
            feature_extractor: Optional[Any] = None,
            image_processor: Optional[Any] = None,
            sample_data: Optional[Any] = None,
            hf_task: Optional[HuggingFaceTask] = None,
            task_type: Optional[TaskType] = None,
            drift_profile: Optional[DriftProfileType] = None,
        ) -> None:
            """Interface for saving HuggingFace models and pipelines

            Args:
                model:
                    Model to associate with interface. This can be a HuggingFace pipeline (inherits from Pipeline),
                    or a HuggingFace model (inherits from PreTrainedModel or TFPreTrainedModel).
                tokenizer:
                    Tokenizer to associate with the model. This must be a HuggingFace tokenizer (PreTrainedTokenizerBase).
                    If using a pipeline that already has a tokenizer, this can be None.
                feature_extractor:
                    Feature extractor to associate with the model. This must be a HuggingFace feature extractor
                    (PreTrainedFeatureExtractor). If using a pipeline that already has a feature extractor,
                    this can be None.
                image_processor:
                    Image processor to associate with the model. This must be a HuggingFace image processor
                    (BaseImageProcessor). If using a pipeline that already has an image processor,
                    this can be None.
                sample_data:
                    Sample data to use to convert to ONNX and make sample predictions. This data must be a
                    HuggingFace-supported type.
                hf_task:
                    HuggingFace task to associate with the model. Defaults to Undefined.
                    Accepted tasks are as follows (taken from HuggingFace pipeline docs):
                        - `"audio-classification"`: will return a [`AudioClassificationPipeline`].
                        - `"automatic-speech-recognition"`: will return a [`AutomaticSpeechRecognitionPipeline`].
                        - `"depth-estimation"`: will return a [`DepthEstimationPipeline`].
                        - `"document-question-answering"`: will return a [`DocumentQuestionAnsweringPipeline`].
                        - `"feature-extraction"`: will return a [`FeatureExtractionPipeline`].
                        - `"fill-mask"`: will return a [`FillMaskPipeline`]:.
                        - `"image-classification"`: will return a [`ImageClassificationPipeline`].
                        - `"image-feature-extraction"`: will return an [`ImageFeatureExtractionPipeline`].
                        - `"image-segmentation"`: will return a [`ImageSegmentationPipeline`].
                        - `"image-text-to-text"`: will return a [`ImageTextToTextPipeline`].
                        - `"image-to-image"`: will return a [`ImageToImagePipeline`].
                        - `"image-to-text"`: will return a [`ImageToTextPipeline`].
                        - `"mask-generation"`: will return a [`MaskGenerationPipeline`].
                        - `"object-detection"`: will return a [`ObjectDetectionPipeline`].
                        - `"question-answering"`: will return a [`QuestionAnsweringPipeline`].
                        - `"summarization"`: will return a [`SummarizationPipeline`].
                        - `"table-question-answering"`: will return a [`TableQuestionAnsweringPipeline`].
                        - `"text2text-generation"`: will return a [`Text2TextGenerationPipeline`].
                        - `"text-classification"` (alias `"sentiment-analysis"` available): will return a
                        [`TextClassificationPipeline`].
                        - `"text-generation"`: will return a [`TextGenerationPipeline`]:.
                        - `"text-to-audio"` (alias `"text-to-speech"` available): will return a [`TextToAudioPipeline`]:.
                        - `"token-classification"` (alias `"ner"` available): will return a [`TokenClassificationPipeline`].
                        - `"translation"`: will return a [`TranslationPipeline`].
                        - `"translation_xx_to_yy"`: will return a [`TranslationPipeline`].
                        - `"video-classification"`: will return a [`VideoClassificationPipeline`].
                        - `"visual-question-answering"`: will return a [`VisualQuestionAnsweringPipeline`].
                        - `"zero-shot-classification"`: will return a [`ZeroShotClassificationPipeline`].
                        - `"zero-shot-image-classification"`: will return a [`ZeroShotImageClassificationPipeline`].
                        - `"zero-shot-audio-classification"`: will return a [`ZeroShotAudioClassificationPipeline`].
                        - `"zero-shot-object-detection"`: will return a [`ZeroShotObjectDetectionPipeline`].
                task_type:
                    The intended task type for the model. Note: This is the OpsML task type, not the HuggingFace task type.
                drift_profile:
                    Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
            """

        def save(
            self,
            path: Path,
            save_kwargs: None | ModelSaveKwargs = None,
        ) -> ModelInterfaceMetadata:
            """Save the HuggingFaceModel interface

            Args:
                path (Path):
                    Base path to save artifacts
                save_kwargs (ModelSaveKwargs):
                    Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                    that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                    the underlying library.

                    - model: Kwargs that will be passed to save_model. See save_model for more details.
                    - preprocessor: Kwargs that will be passed to save_preprocessor
                    - onnx: Kwargs that will be passed when saving the onnx model
                        - For the HuggingFaceModel, this should be an instance of HuggingFaceOnnxArgs
            """

        @property
        def model(self) -> Optional[Any]:
            """Returns as HuggingFace model (PreTrainedModel, TFPreTrainedModel).
            Can be None if the model is a pipeline.
            """

        @model.setter
        def model(self, model: Any) -> None:
            """Sets the model

            Args:
                model:
                    Model to associate with the interface. This must be a HuggingFace model (PreTrainedModel, TFPreTrainedModel).
                    If using a pipeline that already has a model, this can be None.
            """

        @property
        def tokenizer(self) -> Optional[Any]:
            """Returns the tokenizer. Can be None if the model is a pipeline.
            If present, will be of type PreTrainedTokenizerBase
            """

        @tokenizer.setter
        def tokenizer(self, tokenizer: Any) -> None:
            """Sets the tokenizer

            Args:
                tokenizer:
                    Tokenizer to associate with the model. This must be a HuggingFace tokenizer (PreTrainedTokenizerBase).
                    If using a pipeline that already has a tokenizer, this can be None.
            """

        @property
        def image_processor(self) -> Optional[Any]:
            """Returns the image processor. Can be None if the model is a pipeline.
            If present, will be of type BaseImageProcessor
            """

        @image_processor.setter
        def image_processor(self, image_processor: Any) -> None:
            """Sets the image processor

            Args:
                image_processor:
                    Image processor to associate with the model. This must be a HuggingFace image processor
                    (BaseImageProcessor). If using a pipeline that already has an image processor,
                    this can be None.
            """

        @property
        def feature_extractor(self) -> Optional[Any]:
            """Returns the feature extractor. Can be None if the model is a pipeline.
            If present, will be of type PreTrainedFeatureExtractor
            """

        @feature_extractor.setter
        def feature_extractor(self, feature_extractor: Any) -> None:
            """Sets the feature extractor

            Args:
                feature_extractor:
                    Feature extractor to associate with the model. This must be a HuggingFace feature extractor
                    (PreTrainedFeatureExtractor). If using a pipeline that already has a feature extractor,
                    this can be None.
            """

    ```

### Nuts and Bolts

The `HuggingFaceModel` and it's associated model, tokenizer, feature extractor and image processor are saved using the `save_pretrained` method.

### HuggingFace Onnx Args

There are times where you may want to convert your HuggingFace model to onnx format. Unlike other ModelInterfaces, The `HuggingFaceModel` has a special `HuggingFaceOnnxArgs` object that you can into `ModelSaveKwargs`

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**ort_type**</span>       | (`HuggingFaceORTModel`) The ORT model type to use. See below.   |
| <span class="text-alert">**provider**</span>       | Onnx runtime provider to use  |
| <span class="text-alert">**quantize**</span>      | Whether to quantize the model |
| <span class="text-alert">**config**</span>      | Optional Optimum config if quantizing |
| <span class="text-alert">**extra_kwargs**</span>    | Extra kwargs to pass to the onnx conversion |


???success "HuggingFaceORTModel"
    ```python
    class HuggingFaceORTModel:
        OrtAudioClassification: "HuggingFaceORTModel"
        OrtAudioFrameClassification: "HuggingFaceORTModel"
        OrtAudioXVector: "HuggingFaceORTModel"
        OrtCustomTasks: "HuggingFaceORTModel"
        OrtCtc: "HuggingFaceORTModel"
        OrtFeatureExtraction: "HuggingFaceORTModel"
        OrtImageClassification: "HuggingFaceORTModel"
        OrtMaskedLm: "HuggingFaceORTModel"
        OrtMultipleChoice: "HuggingFaceORTModel"
        OrtQuestionAnswering: "HuggingFaceORTModel"
        OrtSemanticSegmentation: "HuggingFaceORTModel"
        OrtSequenceClassification: "HuggingFaceORTModel"
        OrtTokenClassification: "HuggingFaceORTModel"
        OrtSeq2SeqLm: "HuggingFaceORTModel"
        OrtSpeechSeq2Seq: "HuggingFaceORTModel"
        OrtVision2Seq: "HuggingFaceORTModel"
        OrtPix2Struct: "HuggingFaceORTModel"
        OrtCausalLm: "HuggingFaceORTModel"
        OrtOptimizer: "HuggingFaceORTModel"
        OrtQuantizer: "HuggingFaceORTModel"
        OrtTrainer: "HuggingFaceORTModel"
        OrtSeq2SeqTrainer: "HuggingFaceORTModel"
        OrtTrainingArguments: "HuggingFaceORTModel"
        OrtSeq2SeqTrainingArguments: "HuggingFaceORTModel"
        OrtStableDiffusionPipeline: "HuggingFaceORTModel"
        OrtStableDiffusionInpaintPipeline: "HuggingFaceORTModel"
        OrtStableDiffusionXlPipeline: "HuggingFaceORTModel"
        OrtStableDiffusionXlImg2ImgPipeline: "HuggingFaceORTModel"
        OrtStableDiffusionImg2ImgPipeline: "HuggingFaceORTModel"
    ```

???success "HuggingFaceOnnxArgs"
    ```python
    class HuggingFaceOnnxArgs:
        ort_type: HuggingFaceORTModel
        provider: str
        quantize: bool
        export: bool
        config: Optional[Any]
        extra_kwargs: Optional[Dict[str, Any]]

        def __init__(
            self,
            ort_type: HuggingFaceORTModel,
            provider: str,
            quantize: bool = False,
            config: Optional[Any] = None,
            extra_kwargs: Optional[Dict[str, Any]] = None,
        ) -> None:
            """Optional Args to use with a huggingface model

            Args:
                ort_type:
                    Optimum onnx class name
                provider:
                    Onnx runtime provider to use
                config:
                    Optional optimum config to use
                quantize:
                    Whether to quantize the model
                extra_kwargs:
                    Extra kwargs to pass to the onnx conversion (save_pretrained method for ort models)

            """
    ```

## CatBoostModel

Interface for saving a CatBoost model

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/catboost_model.py)

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be an `CatBoost` model  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

???success "CatBoostModel"
    ```python
    class CatBoostModel(ModelInterface):
        def __init__(
            self,
            model: Optional[Any] = None,
            preprocessor: Optional[Any] = None,
            sample_data: Optional[Any] = None,
            task_type: Optional[TaskType] = None,
            drift_profile: Optional[DriftProfileType] = None,
        ) -> None:
            """Interface for saving CatBoost models

            Args:
                model:
                    Model to associate with the interface. This model must be a CatBoost model.
                preprocessor:
                    Preprocessor to associate with the model.
                sample_data:
                    Sample data to use to make predictions.
                task_type:
                    The type of task the model performs
                drift_profile:
                    Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
            """

        @property
        def preprocessor(self) -> Optional[Any]:
            """Returns the preprocessor"""

        @preprocessor.setter
        def preprocessor(self, preprocessor: Any) -> None:
            """Sets the preprocessor

            Args:
                preprocessor:
                    Preprocessor to associate with the model. This preprocessor must be from the
                    scikit-learn ecosystem
            """

        @property
        def preprocessor_name(self) -> Optional[str]:
            """Returns the preprocessor name"""
    ```

### Nuts and Bolts

CatBoost models are saved via `save_model` which exports a `.cbm` file. Preprocessors are saved via `joblib`.

## TorchModel

Interface for saving a CatBoost model

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/torch_model.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be of type `torch.nn.Module`  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |


???success "TorchModel"
    ```python
    class TorchModel(ModelInterface):
        def __init__(
            self,
            model: Optional[Any] = None,
            preprocessor: Optional[Any] = None,
            sample_data: Optional[Any] = None,
            task_type: Optional[TaskType] = None,
            drift_profile: Optional[DriftProfileType] = None,
        ) -> None:
            """Interface for saving PyTorch models

            Args:
                model:
                    Model to associate with interface. This model must inherit from torch.nn.Module.
                preprocessor:
                    Preprocessor to associate with model.
                sample_data:
                    Sample data to use to convert to ONNX and make sample predictions. This data must be a
                    pytorch-supported type. TorchData interface, torch tensor, torch dataset, Dict[str, torch.Tensor],
                    List[torch.Tensor], Tuple[torch.Tensor].
                task_type:
                    The intended task type of the model.
                drift_profile:
                    Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
            """

        @property
        def preprocessor(self) -> Optional[Any]:
            """Returns the preprocessor"""

        @preprocessor.setter
        def preprocessor(self, preprocessor: Any) -> None:
            """Sets the preprocessor

            Args:
                preprocessor:
                    Preprocessor to associate with the model. This preprocessor must be from the
                    scikit-learn ecosystem
            """

        @property
        def preprocessor_name(self) -> Optional[str]:
            """Returns the preprocessor name"""

        def save(
            self,
            path: Path,
            save_kwargs: None | ModelSaveKwargs = None,
        ) -> ModelInterfaceMetadata:
            """Save the TorchModel interface. Torch models are saved
            as state_dicts as is the standard for PyTorch.

            Args:
                path (Path):
                    Base path to save artifacts
                save_kwargs (ModelSaveKwargs):
                    Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                    that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                    the underlying library.
            """
    ```

### Nuts and Bolts

The following steps are executed when saving a TorchModel:

### Saving a Model

- The state dict of the model is extracted from `state_dict()` 
- The sate dict is saved to a `.pt` file using `torch.save`
- If any user-defined save kwargs are passed using `ModelSaveKwargs`, they are passed to the `torch.save` method as a dictionary.

### Loading a Model

- As a result of the model being saved as a state dict, a user will need to supply the model call as a load kwarg when loading the model.
- The state dict is loaded from path and then loaded into the model using Torch's `load_state_dict()` method.
- If any user-defined load kwargs are passed using `ModelLoadKwargs`, they are passed to the `torch.load` method as a dictionary.

```python

class Polynomial3(torch.nn.Module):
    def __init__(self):
        """
        In the constructor we instantiate four parameters and assign them as
        member parameters.
        """
        super().__init__()
        self.x1 = torch.nn.Parameter(torch.randn(()))
        self.x2 = torch.nn.Parameter(torch.randn(()))

    def forward(self, x1: torch.Tensor, x2: torch.Tensor):
        """
        In the forward function we accept a Tensor of input data and we must return
        a Tensor of output data. We can use Modules defined in the constructor as
        well as arbitrary operators on Tensors.
        """
        return self.x1 + self.x2 * x1 * x2

model = Polynomial3()

# ... logic to load from registry

# load the model
modelcard.load(load_kwargs = ModelLoadKwargs(model={"model": model})) #(1)
```

1. The model object is passed as a load kwarg when loading a `ModelCard's` components


## LightningModel

Interface for saving a Lightning model

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/lightning_model.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**trainer**</span>       | A model trainer to associate with interface. This model must be of type `lightning.Trainer`  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |


???success "LightningModel"
    ```python
    class LightningModel(ModelInterface):
        def __init__(
            self,
            trainer: Optional[Any] = None,
            preprocessor: Optional[Any] = None,
            sample_data: Optional[Any] = None,
            task_type: Optional[TaskType] = None,
            drift_profile: Optional[DriftProfileType] = None,
        ) -> None:
            """Interface for saving PyTorch Lightning models

            Args:
                trainer:
                    Pytorch lightning trainer to associate with interface.
                preprocessor:
                    Preprocessor to associate with model.
                sample_data:
                    Sample data to use to convert to ONNX and make sample predictions. This data must be a
                    pytorch-supported type. TorchData interface, torch tensor, torch dataset, Dict[str, torch.Tensor],
                    List[torch.Tensor], Tuple[torch.Tensor].
                task_type:
                    The intended task type of the model.
                drift_profile:
                    Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
            """

        @property
        def trainer(self) -> None:
            """Returns the trainer"""

        @trainer.setter
        def trainer(self, trainer: Any) -> None:
            """Sets the trainer"""

        @property
        def preprocessor(self) -> Optional[Any]:
            """Returns the preprocessor"""

        @preprocessor.setter
        def preprocessor(self, preprocessor: Any) -> None:
            """Sets the preprocessor

            Args:
                preprocessor:
                    Preprocessor to associate with the model. This preprocessor must be from the
                    scikit-learn ecosystem
            """

        @property
        def preprocessor_name(self) -> Optional[str]:
            """Returns the preprocessor name"""

        def save(
            self,
            path: Path,
            save_kwargs: None | ModelSaveKwargs = None,
        ) -> ModelInterfaceMetadata:
            """Save the LightningModel interface. Lightning models are saved via checkpoints.

            Args:
                path (Path):
                    Base path to save artifacts
                save_kwargs (ModelSaveKwargs):
                    Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                    that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                    the underlying library.

                    - model: Kwargs that will be passed to save_model. See save_model for more details.
                    - preprocessor: Kwargs that will be passed to save_preprocessor
                    - onnx: Kwargs that will be passed to save_onnx_model. See convert_onnx_model for more details.
            """
    ```

### Nuts and Bolts

The following steps are executed when saving a LightningModel:

### Saving a Model

- Lightning models are saved via checkpoints and the `save_checkpoint` method, which exports a `.ckpt` file. Thus, make sure the trainer is stopped at the appropriate checkpoint, or reverted to your preferred checkpoint prior to saving.

### Loading a Model

- When loading a LightningModel, the model is loaded from the saved `Trainer` checkpoint.
- Similar to `TorchModel`, an instantiated model object is required to be passed as a load kwarg
- The saved checkpoint is then loaded into the model using the `load_from_checkpoint` method including any additional kwargs that are passed via `ModelLoadKwargs`.
- The model can then be accessed via the `model` property of `LightningModel`.


## TensorFlowModel

Interface for saving a TensorFlow model


**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/tensorflow_model.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be of type `tensorflow.keras.Model`  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |


???success "TensorFlowModel"
    ```python
    class TensorFlowModel(ModelInterface):
        def __init__(
            self,
            model: Optional[Any] = None,
            preprocessor: Optional[Any] = None,
            sample_data: Optional[Any] = None,
            task_type: Optional[TaskType] = None,
            schema: Optional[FeatureSchema] = None,
            drift_profile: Optional[DriftProfileType] = None,
        ) -> None:
            """Interface for saving PyTorch models

            Args:
                model:
                    Model to associate with interface. This model must inherit from tensorflow.keras.Model
                preprocessor:
                    Preprocessor to associate with model.
                sample_data:
                    Sample data to use to convert to ONNX and make sample predictions. This data must be a
                    tensorflow-supported type. numpy array, tf.Tensor, torch dataset, Dict[str, tf.Tensor],
                    List[tf.Tensor], Tuple[tf.Tensor].
                task_type:
                    The intended task type of the model.
                drift_profile:
                    Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
            """

        @property
        def preprocessor(self) -> Optional[Any]:
            """Returns the preprocessor"""

        @preprocessor.setter
        def preprocessor(self, preprocessor: Any) -> None:
            """Sets the preprocessor

            Args:
                preprocessor:
                    Preprocessor to associate with the model
            """

        @property
        def preprocessor_name(self) -> Optional[str]:
            """Returns the preprocessor name"""
    ```

### Nuts and Bolts

The model is saved using the preferred **keras** format via `model.save`. Loading is done through `tensorflow.keras.models` `load_model` method. If a user provides a custom load kwarg, it is passed to the `load_model` method as a dictionary


### Onnx Model

As mention elsewhere, all supported model interfaces can be automatically converted to onnx format. However, you may find that you only want to save the convert onnx model. In this case, you can leverage the `OnnxModel` interface for saving an onnx model directly.

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Onnx model to associate with the interface. This model must be an Onnx ModelProto  |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/onnx_model.py)

???success "OnnxModel"
    ```python
    class OnnxModel(ModelInterface):
        def __init__(
            self,
            model: Optional[Any] = None,
            sample_data: Optional[Any] = None,
            task_type: Optional[TaskType] = None,
            drift_profile: Optional[DriftProfileType] = None,
        ) -> None:
            """Interface for saving an OnnxModel

            Args:
                model:
                    Onnx model to associate with the interface. This model must be an Onnx ModelProto
                sample_data:
                    Sample data to use to make predictions
                task_type:
                    The type of task the model performs
                drift_profile:
                    Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile

            Example:
                ```python
                from sklearn.datasets import load_iris  # type: ignore
                from sklearn.model_selection import train_test_split  # type: ignore
                from sklearn.ensemble import RandomForestClassifier  # type: ignore
                from skl2onnx import to_onnx  # type: ignore
                import onnxruntime as rt  # type: ignore

                iris = load_iris()

                X, y = iris.data, iris.target
                X = X.astype(np.float32)
                X_train, X_test, y_train, y_test = train_test_split(X, y)
                clr = RandomForestClassifier()
                clr.fit(X_train, y_train)

                onx = to_onnx(clr, X[:1])

                interface = OnnxModel(model=onx, sample_data=X_train)
                ```
            """

        @property
        def session(self) -> OnnxSession:
            """Returns the onnx session. This will error if the OnnxSession is not set"""
    ```

### Nuts and Bolts

`OnnxModel` uses the onnxruntime library to save and load the model. Input and out schema are derived using the [ort](https://github.com/pykeio/ort) crate.

## CustomModel

While the above interfaces cover the most common use cases, there may be times where you want to create your own custom model interface. By design, the `ModelInterface` can be subclassed in cases where a more flexible implementation is needed. However to make sure all other components work nicely together, you will need to implement the following.


**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/model/custom_model.py)

### Custom Save

- **save**: This method is called when saving the model. It should save the model and any other artifacts to the specified path. The method should return a `ModelInterfaceMetadata` object.

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**path**</span>       | The base path to save artifacts to. **note** - this is typically injected at the time of saving. See the below example for how it should be used |
| <span class="text-alert">**save_kwargs**</span>       | Optional ModelSaveKwargs to use when saving the model |


```python
class CustomInterface(ModelInterface): #(1)
    def save( #(2)
        self,
        path: Path, 
        save_kwargs: ModelSaveKwargs | None = None,
    ) -> ModelInterfaceMetadata:

        model_save_path = Path("model").with_suffix(".joblib") #(3)

        joblib.dump(self.model, path / model_save_path) #(4)

        save_metadata = ModelInterfaceSaveMetadata(model_uri=model_save_path)  #(5)


        return ModelInterfaceMetadata( #(5)
            task_type=self.task_type,
            model_type=self.model_type,
            data_type=self.data_type,
            save_metadata=save_metadata,
            extra_metadata={"foo": "bar"},
        )
```

1. The class must inherit from `ModelInterface`. This is the base class for all model interfaces.
2. The `save` method arguments cannot be changed. These are standardized across all interfaces and are used internally within the Rust runtime.
3. The `model_save_path` is the path to save the model to relative to the base path. This will be joined with the base path when saving and loading the model.
4. The model is saved using `joblib.dump` to the specified path. This is where you would save your model and any other artifacts.
5. `ModelInterfaceSaveMetadata` is a core component for storing artifact uris and extra metadata. It is **required** as it is used internally to load artifacts.
6. The `ModelInterfaceMetadata` is returned from the save method. This is **required**.

???success "DataProcessor"
    ```python
    class DataProcessor:
        """Generic class that holds uri information for data preprocessors and postprocessors"""

        name: str
        uri: Path
        type: ProcessorType

        def __str__(self): ...
    ```

???success "ModelInterfaceSaveMetadata"
    ```python
    class ModelInterfaceSaveMetadata:
        model_uri: Path
        data_processor_map: Dict[str, DataProcessor]
        sample_data_uri: Path
        onnx_model_uri: Optional[Path]
        drift_profile_uri_map: Optional[Dict[str, DriftProfileUri]]
        extra: Optional[ExtraMetadata]
        save_kwargs: Optional[ModelSaveKwargs]

        def __init__(
            self,
            model_uri: Path,
            data_processor_map: Optional[Dict[str, DataProcessor]] = {},  # type: ignore
            sample_data_uri: Optional[Path] = None,
            onnx_model_uri: Optional[Path] = None,
            drift_profile_uri_map: Optional[Dict[str, DriftProfileUri]] = None,
            extra: Optional[ExtraMetadata] = None,
            save_kwargs: Optional[ModelSaveKwargs] = None,
        ) -> None:
            """Define model interface save arguments

            Args:
                model_uri:
                    Path to the model
                data_processor_map:
                    Dictionary of data processors
                sample_data_uri:
                    Path to the sample data
                onnx_model_uri:
                    Path to the onnx model
                drift_profile_uri_map:
                    Dictionary of drift profiles
                extra_metadata:
                    Extra metadata
                save_kwargs:
                    Optional save args
            """

        def __str__(self): ...
        def model_dump_json(self) -> str: ...
    ```

???success "ModelInterfaceMetadata"
    ```python
    class ModelInterfaceMetadata:
        task_type: TaskType
        model_type: ModelType
        data_type: DataType
        onnx_session: Optional[OnnxSession]
        schema: FeatureSchema
        save_metadata: ModelInterfaceSaveMetadata
        extra_metadata: dict[str, str]

        def __init__(
            self,
            save_metadata: ModelInterfaceSaveMetadata,
            task_type: TaskType = TaskType.Undefined,
            model_type: ModelType = ModelType.Unknown,
            data_type: DataType = DataType.NotProvided,
            schema: FeatureSchema = FeatureSchema(),
            onnx_session: Optional[OnnxSession] = None,
            extra_metadata: dict[str, str] = {},
        ) -> None:
            """Define a model interface

            Args:
                task_type:
                    Task type
                model_type:
                    Model type
                data_type:
                    Data type
                onnx_session:
                    Onnx session
                schema:
                    Feature schema
                data_type:
                    Sample data type
                save_metadata:
                    Save metadata
                extra_metadata:
                    Extra metadata. Must be a dictionary of strings
            """

        def __str__(self) -> str:
            """Return the string representation of the model interface metadata"""

        def model_dump_json(self) -> str:
            """Dump the model interface metadata to json"""

        @staticmethod
        def model_validate_json(json_string: str) -> "ModelInterfaceMetadata":
            """Validate the model interface metadata json"""
    ```

### Custom Load

To load a custom model, you will need to implement the `load` method. This method is called when loading the model. It should load the model and any other artifacts from the specified path.

- **load**: This method is called when loading the model

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**path**</span>       | The base path to load artifacts from. **note** - this is typically injected at the time of loading. See the below example for how it should be used |
| <span class="text-alert">**metadata**</span>       | `ModelInterfaceSaveMetadata`. This will be injected by Opsml when the card is loaded from a registry  |
| <span class="text-alert">**load_kwargs**</span>       | Optional `ModelLoadKwargs`. Additional load kwargs used to load a model and it's artifacts |

```python
class CustomInterface(ModelInterface):
    def load(
        self,
        path: Path,
        metadata: ModelInterfaceSaveMetadata,
        load_kwargs: ModelLoadKwargs | None = None,
    ) -> None:
        model_path = path / metadata.model_uri #(1)
        self.model = joblib.load(model_path) #(2)
```

1. We use the `metadata` object to get the model path or any other path to an artifact. It is then joined with the base path to load the model.
2. The model is loaded using `joblib.load` and assigned to the model property of the interface. This is where you would load your model and any other artifacts.

### Changing Init Arguments

If you find in your custom interface that you are changing class/self attributes during instantiation, you will also need to include two extra methods called `from_metadata` (staticmethod) as well as a `__new__` method. The reason for this is (1), pyo3 does not currently support custom `__init__` methods (2) `from_metadata` is called on all interfaces when loading a card from the registry and is used to initialize the class with metadata attributes.

The below example shows an example of how you can implement this. In the example, we are adding the `preprocessor` attribute

```python
class CustomModel(ModelInterface):
    def __new__( #(1)
        cls,
        preprocessor=None, #(2)
        model: None | Any = None,
        sample_data: None | Any = None,
        task_type: None | TaskType = None,
    ):
        instance = super(CustomModel, cls).__new__(
            cls,
            model=model,
            sample_data=sample_data,
            task_type=task_type,
        )

        return instance

    def __init__(self, preprocessor, model, sample_data, task_type):
        """Init method for the custom model interface."""

        super().__init__()

        self.preprocessor = preprocessor #(3)

    def save(self, path, save_kwargs=None):
        ...

    def load(self, path, metadata, load_kwargs=None):
        ...

    @staticmethod
    def from_metadata(metadata: ModelInterfaceMetadata) -> "CustomModel":
        """Load model from metadata."""

        return CustomModel(
            model=None,
            sample_data=None,
            task_type=metadata.task_type,
            preprocessor=None,
        )
```

1. Custom __new__ method
2. Adding preprocessor as a class argument
3. Assigning preprocessor to the class attribute

**Note**: If you are not changing the default class attributes, you do not need to to implement `__new__` or `from_metadata`.


### Method Overriding Checklist

| Changing Class Attributes? | Methods to Implement |
| -------------------------- | -------------------- |
| <span class="text-alert">**No**</span> | `save`, `load`       |
| <span class="text-alert">**Yes**</span> | `save`, `load`, `__new__`, `from_metadata` |

### Loading from a Registry

To load a custom interface from the registry, you will need to supply the python definition of the interface class to the `load_card` method. This is important to keep in mind for reproducibility and sharing. Another user will not be able to use your interface unless they have the same class definition.

```python

class MyCustomInterface(ModelInterface):
    ...

registry.load_card(uid="{{model uid}}", interface=MyCustomInterface) #(1)
```

1. The interface class is passed to the `load_card` method. This is required for custom interfaces