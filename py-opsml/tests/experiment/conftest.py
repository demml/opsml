from typing import Tuple, cast
import pytest
import pandas as pd
from sklearn import ensemble  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from opsml.model import SklearnModel, TaskType
from opsml.helpers.data import create_fake_data
from opsml.data import PandasData, DataSplit, ColumnSplit, ColType


@pytest.fixture(scope="session")
def example_dataframe() -> (
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
):
    X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

    return X, y, X, y


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
