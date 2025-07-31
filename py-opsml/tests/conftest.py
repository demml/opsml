import pytest

from opsml.model import Feature
from opsml.logging import RustyLogger, LoggingConfig, LogLevel
from opsml.mock import RegistryTestHelper
from opsml.llm import Prompt
from typing import Tuple, Dict
from pydantic import BaseModel
import sys
import platform
from opsml import ModelInterface
from opsml.model import (
    ModelInterfaceSaveMetadata,
    ModelInterfaceMetadata,
    DataProcessor,
    ProcessorType,
)
from typing import cast
import pandas as pd
from pathlib import Path
from opsml.model import SklearnModel, TaskType
from opsml.data import PandasData
from opsml.helpers.data import create_fake_data  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn import ensemble  # type: ignore
from opsml.data import ColType, ColumnSplit, DataSplit
import joblib  # type: ignore

DARWIN_EXCLUDE = sys.platform == "darwin" and platform.machine() == "arm64"
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


# Sets up logging for tests
RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Debug))


class MockInterface(BaseModel):
    is_interface: bool = True


class CustomModel(ModelInterface):
    def __new__(cls, preprocessor=None, **kwargs):
        instance = super(CustomModel, cls).__new__(
            cls,
            **kwargs,
        )

        return instance

    def __init__(self, preprocessor, **kwargs):
        """Init method for the custom model interface."""

        super().__init__()

        self.preprocessor = preprocessor

    def save(self, path, save_kwargs=None):
        """Custom save method for the model interface.

        Args:
            path (Path): Path to save the model.
            save_kwargs (ModelSaveKwargs): Save kwargs for the model.

        """
        model_save_path = Path("model").with_suffix(".joblib")
        preprocessor_save_path = Path("preprocessor").with_suffix(".joblib")

        assert self.model is not None
        joblib.dump(self.model, path / model_save_path)

        assert self.preprocessor is not None
        joblib.dump(self.preprocessor, path / preprocessor_save_path)

        save_metadata = ModelInterfaceSaveMetadata(
            model_uri=model_save_path,
            data_processor_map={
                "preprocessor": DataProcessor(
                    name="preprocessor",
                    uri=preprocessor_save_path,
                    type=ProcessorType.Preprocessor,
                )
            },
        )

        return ModelInterfaceMetadata(
            task_type=self.task_type,
            model_type=self.model_type,
            data_type=self.data_type,
            save_metadata=save_metadata,
        )

    def load(self, path, metadata, load_kwargs=None):
        """Custom load method for the model interface."""
        model_path = path / metadata.model_uri
        preprocessor_path = path / metadata.data_processor_map["preprocessor"].uri

        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)

    # staticmethod to load from metadata
    @staticmethod
    def from_metadata(metadata: ModelInterfaceMetadata) -> "CustomModel":
        """Load model from metadata."""

        return CustomModel(
            model=None,
            sample_data=None,
            task_type=metadata.task_type,
            preprocessor=None,
        )


class IncorrectCustomModel(ModelInterface):
    def save(self, path, save_kwargs=None):
        """Custom save method for the model interface.

        Args:
            path (Path): Path to save the model.
            save_kwargs (ModelSaveKwargs): Save kwargs for the model.

        """
        model_save_path = Path("model").with_suffix(".joblib")
        preprocessor_save_path = Path("preprocessor").with_suffix(".joblib")

        assert self.model is not None
        joblib.dump(self.model, path / model_save_path)

        # Incorrectly saving the preprocessor (this doesnt exist, should cause error)
        assert self.preprocessor is not None
        joblib.dump(self.preprocessor, path / preprocessor_save_path)

        save_metadata = ModelInterfaceSaveMetadata(
            model_uri=model_save_path,
            data_processor_map={
                "preprocessor": DataProcessor(
                    name="preprocessor",
                    uri=preprocessor_save_path,
                    type=ProcessorType.Preprocessor,
                )
            },
        )

        return ModelInterfaceMetadata(
            task_type=self.task_type,
            model_type=self.model_type,
            data_type=self.data_type,
            save_metadata=save_metadata,
        )


@pytest.fixture
def card_args() -> Tuple[Dict[str, Feature], Dict[str, str]]:
    Feature_map = {"Feature1": Feature("type1", [1, 2, 3], {"arg1": "value1"})}
    metadata = {"key1": "value1"}
    return Feature_map, metadata


@pytest.fixture
def mock_interface(
    card_args: Tuple[Dict[str, Feature], Dict[str, str]],
) -> MockInterface:
    Feature_map, metadata = card_args
    return MockInterface()


@pytest.fixture
def mock_db():
    helper = RegistryTestHelper()

    helper.setup()

    yield

    helper.cleanup()


@pytest.fixture
def pandas_data(example_dataframe) -> PandasData:
    split = DataSplit(
        label="train",
        column_split=ColumnSplit(
            column_name="col_1",
            column_value=0.4,
            column_type=ColType.Builtin,
            inequality="<=",
        ),
    )

    X_train, _, _, _ = example_dataframe
    return PandasData(
        data=X_train,
        data_splits=[split],
        dependent_vars=["col_2"],
    )


@pytest.fixture
def example_dataframe() -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

    return X, y, X, y


@pytest.fixture
def random_forest_classifier(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X_train.to_numpy(), y_train)

    return SklearnModel(
        model=reg,
        sample_data=X_train,
        task_type=TaskType.Classification,
        preprocessor=StandardScaler(),
    )


@pytest.fixture
def custom_interface(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X_train.to_numpy(), y_train)

    return CustomModel(
        model=reg,
        sample_data=X_train,
        task_type=TaskType.AnomalyDetection,
        preprocessor=StandardScaler(),
    )


@pytest.fixture
def incorrect_custom_interface(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X_train.to_numpy(), y_train)

    return IncorrectCustomModel(model=reg)


@pytest.fixture
def chat_prompt() -> Prompt:
    prompt = Prompt(
        model="gpt-4o",
        user_message="what is 2 + 2?",
        provider="openai",
        system_message="You are a helpful assistant.",
    )
    return prompt
