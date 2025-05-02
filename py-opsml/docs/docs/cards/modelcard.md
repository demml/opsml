
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

### Default Save Method

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

???success "Py Doc"
    ```python
    class ModelSaveKwargs:
        def __init__(
            self,
            onnx: Optional[Dict | HuggingFaceOnnxArgs] = None,
            model: Optional[Dict] = None,
            preprocessor: Optional[Dict] = None,
        ) -> None:
            """Optional arguments to pass to save_model

            Args:
                onnx (Dict or HuggingFaceOnnxArgs):
                    Optional onnx arguments to use when saving model to onnx format
                model (Dict):
                    Optional model arguments to use when saving
                preprocessor (Dict):
                    Optional preprocessor arguments to use when saving
            """

        def __str__(self): ...
        def model_dump_json(self) -> str: ...
        @staticmethod
        def model_validate_json(json_string: str) -> "ModelSaveKwargs": ...
    ```





## SklearnModel

Interface for saving an Sklearn model

**Example**: [`Link`](https://github.com/opsml/py-opsml/examples/model/sklean.py)


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


## LightGBMModel

Interface for saving a LightGBM Booster model. **Note** - If using a LGBMRegressor or LGBMClassifier, you should use the SklearnModelInterface instead.


**Example**: [`Link`](https://github.com/opsml/py-opsml/examples/model/lightgbm_booster.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be an lightgbm booster  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model. Preprocessor to associate with the model  |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |


???success "Py Doc"
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


**Example**: [`Link`](https://github.com/opsml/py-opsml/examples/model/xgb_booster.py)


| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**model**</span>       | Model to associate with interface. This model must be an xgboost booster  |
| <span class="text-alert">**preprocessor**</span>       | Optional preprocessor to associate with the model. Preprocessor to associate with the model  |
| <span class="text-alert">**sample_data**</span>      | Optional ample of data that is fed to the model at inference time |
| <span class="text-alert">**task_type**</span>    | Optional task type of the model. Defaults to `TaskType.Undefined` |
| <span class="text-alert">**drift_profile**</span> | Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface. |

???success "Py Doc"
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

**Example**: [`Link`](https://github.com/opsml/py-opsml/examples/model/hf_model.py)


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


???success "Py Doc"
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
            to_onnx: bool = False,
            save_kwargs: None | ModelSaveKwargs = None,
        ) -> ModelInterfaceMetadata:
            """Save the HuggingFaceModel interface

            Args:
                path (Path):
                    Base path to save artifacts
                to_onnx (bool):
                    Whether to save the model/pipeline to onnx
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