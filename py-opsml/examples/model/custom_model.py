from pathlib import Path
from typing import Dict, Optional, Tuple, cast

import joblib  # type: ignore
import polars as pl  # type: ignore
from opsml import CardRegistry, ModelCard, ModelInterface, RegistryType, TaskType
from opsml.helpers.data import create_fake_data
from opsml.model import (
    DataProcessor,
    ModelInterfaceMetadata,
    ModelInterfaceSaveMetadata,
    ProcessorType,
)
from sklearn.linear_model import LinearRegression  # type: ignore
from sklearn.preprocessing import Binarizer  # type: ignore


class ConstantOffsetRegressor(LinearRegression):
    """A custom sklearn model that adds a constant offset to predictions.

    This is meant to be an used in a custom interface.

    Note: This model would still be compatible with the SklearnModel interface.
    """

    def __init__(self, offset=1.0, **kwargs):
        self.offset = offset

        super().__init__(**kwargs)

    def predict(self, X):
        """Make predictions with an added constant offset."""

        base_predictions = self.predict(X)

        return base_predictions + self.offset


class CustomSklearnInterface(ModelInterface):
    def __new__(
        cls,
        model: Optional[ConstantOffsetRegressor] = None,
        binarizer: Optional[Binarizer] = None,
        task_type: Optional[TaskType] = None,
    ):
        instance = super(CustomSklearnInterface, cls).__new__(
            cls,
            model=model,
            task_type=task_type,
        )

        return instance

    def __init__(
        self,
        model: Optional[ConstantOffsetRegressor] = None,
        binarizer: Optional[Binarizer] = None,
        task_type: Optional[TaskType] = None,
    ):
        """Init method for the custom model interface."""

        super().__init__()

        # adding new attribute to interface
        self.binarizer = binarizer

    def get_model_params(self) -> Dict[str, str]:
        """Get model parameters. This is to demonstrate how you can
        add extra metadata to the ModelInterfaceMetadata"""
        model = cast(ConstantOffsetRegressor, self.model)

        extra = {
            "intercept": str(model.intercept_),
            "offset": str(model.offset),
        }

        return extra

    def save(self, path, save_kwargs=None):
        """Custom save method for the model interface.

        Args:
            path (Path):
                Path to save the model.
            save_kwargs (ModelSaveKwargs):
                Save kwargs for the model.

        """

        # set model save path
        model_save_path = Path("model").with_suffix(".joblib")

        # set binarizer save path
        binarizer_save_path = Path("binarizer").with_suffix(".joblib")

        # save model and binarizer
        assert self.model is not None
        joblib.dump(self.model, path / model_save_path)

        assert self.binarizer is not None
        joblib.dump(self.binarizer, path / binarizer_save_path)

        # create save metadata for model and binarizer
        save_metadata = ModelInterfaceSaveMetadata(
            model_uri=model_save_path,
            data_processor_map={
                "binarizer": DataProcessor(
                    name="binarizer",
                    uri=binarizer_save_path,
                    type=ProcessorType.Preprocessor,
                )
            },
        )

        # create model interface metadata
        return ModelInterfaceMetadata(
            task_type=self.task_type,
            model_type=self.model_type,
            data_type=self.data_type,
            save_metadata=save_metadata,
            extra_metadata=self.get_model_params(),  # add extra metadata
        )

    def load(self, path: Path, metadata: ModelInterfaceSaveMetadata, load_kwargs=None):
        """Custom load method for the model interface."""
        model_path = path / metadata.model_uri
        binarizer_path = path / metadata.data_processor_map["binarizer"].uri

        self.model = joblib.load(model_path)
        self.binarizer = joblib.load(binarizer_path)

    @staticmethod
    def from_metadata(metadata: ModelInterfaceMetadata) -> "CustomSklearnInterface":
        """Load interface from metadata. This is only used to instantiate the class.
        It does not load the model or binarizer.

        Args:
            metadata (ModelInterfaceMetadata):
                Metadata to load the model from.

        """

        return CustomSklearnInterface(
            model=None,
            binarizer=None,
            task_type=metadata.task_type,
        )


### Example usage
registry = CardRegistry(registry_type=RegistryType.Model)


X_train, y_train = cast(Tuple[pl.DataFrame, pl.DataFrame], create_fake_data(n_samples=1200, to_polars=True))

model = ConstantOffsetRegressor(offset=2.0)
binarizer = Binarizer()

# transform the data
transformed = binarizer.fit_transform(X_train.to_numpy())

# fit the data
model.fit(transformed, y_train.to_numpy().ravel())


# create model interface
model_interface = CustomSklearnInterface(
    model=model,
    binarizer=binarizer,
    task_type=TaskType.Regression,
)

# create model card
modelcard = ModelCard(
    interface=model_interface,
    space="opsml",
    name="my_model",
    tags=["foo:bar", "baz:qux"],
)

# register model card
registry.register_card(modelcard)

# list model card
modelcard_list = registry.list_cards(uid=modelcard.uid).as_table()

# load model card
loaded_modelcard: ModelCard = registry.load_card(
    uid=modelcard.uid,
    interface=CustomSklearnInterface,
)

# load model card artifacts
loaded_modelcard.load()

# assert loaded model card
assert loaded_modelcard.interface.model is not None
assert loaded_modelcard.interface.binarizer is not None
