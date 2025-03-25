import pytest

from opsml.core import Feature, RustyLogger, LoggingConfig, LogLevel
from opsml.card import RegistryTestHelper
from opsml.potato_head import Prompt
from typing import Tuple, Dict
from pydantic import BaseModel
import sys
import platform

from typing import cast
import pandas as pd
from opsml.model import SklearnModel, TaskType
from opsml.data import PandasData
from opsml.helpers.data import create_fake_data  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn import ensemble  # type: ignore
from opsml.data import ColType, ColumnSplit, DataSplit


DARWIN_EXCLUDE = sys.platform == "darwin" and platform.machine() == "arm64"
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


# Sets up logging for tests
RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Debug))


class MockInterface(BaseModel):
    is_interface: bool = True


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
def example_dataframe() -> (
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
):
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
def chat_prompt() -> Prompt:
    prompt = Prompt(
        model="gpt-4o",
        prompt="what is 2 + 2?",
        system_prompt="You are a helpful assistant.",
    )
    return prompt
