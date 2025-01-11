import pytest
from typing import Tuple
from sklearn import linear_model  # type: ignore
import numpy as np
from opsml.model import SklearnModel, TaskType
from opsml.data import NumpyData
from opsml.helpers.data import create_fake_data
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn import ensemble


@pytest.fixture(scope="session")
def example_dataframe():
    X, y = create_fake_data(n_samples=1200)

    return X, y, X, y


@pytest.fixture
def regression_data() -> Tuple[np.ndarray, np.ndarray]:
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3

    return X, y


@pytest.fixture
def linear_regression(regression_data) -> Tuple[SklearnModel, NumpyData]:
    X, y = regression_data
    reg = linear_model.LinearRegression().fit(X, y)
    return SklearnModel(model=reg, sample_data=X), NumpyData(data=X)


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
