
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

model_interface.create_drift_profile(X)

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

## How it all works

As you can tell in the example above, `ModelCards` are created by passing in a `ModelInterface`, some required args and some optional args. The `ModelInterface` is the interface is a library-specific interface for saving and extracting metadata from the model. It also allows us to standardize how models are saved (by following the library's guidelines) and ensures reproducibility.

## Model Interface

The `ModelInterface` is the primary interface for working with models in `Opsml`. It is designed to be subclassed and can be used to store models in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `SklearnModel`: Stores data from a sklearn model
- `TorchModel`: Stores data from a pytorch model
- `LightningModel`: Stores data from a pytorch lightning model
- `HuggingFaceModel`: Stores data from a huggingface model
- `TensorFlowModel`: Stores data from a tensorflow model
- `XGBoostModel`: Stores data from a xgboost model
- `LightGBMModel`: Stores data from a lightgbm model
- `CatBoostModel`: Stores data from a catboost model

### Shared Arguments for all ModelInterfaces

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface  |
| <span class="text-alert">**sample_data**</span>  | Optional sample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

???success "Py Doc"
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
        data: CustomMetric | List[CustomMetric],
        config: CustomMetricDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> CustomDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: SpcDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: PsiDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> PsiDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        data: Any,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    def create_drift_profile(  # type: ignore
        self,
        data: Any,
        config: None | SpcDriftConfig | PsiDriftConfig | CustomMetricDriftConfig = None,
        data_type: None | DataType = None,
    ) -> Any:
        """Create a drift profile and append it to the drift profile list

        Args:
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
        to_onnx: bool = False,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the model interface

        Args:
            path (Path):
                Path to save the model
            to_onnx (bool):
                Whether to save the model to onnx
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
        onnx: bool = False,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelInterface components

        Args:
            path (Path):
                Path to load the model
            metadata (ModelInterfaceSaveMetadata):
                Metadata to use to load the model
            onnx (bool):
                Whether to load the onnx model
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


## SklearnModel

Interface for saving an Sklearn model

**Example**: [`Link`](https://github.com/shipt/opsml/blob/main/examples/sklearn/basic.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be from the scikit-learn ecosystem (BaseEstimator)  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model. This preprocessor must be from the  scikit-learn ecosystem  |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

???success "Py Doc"
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