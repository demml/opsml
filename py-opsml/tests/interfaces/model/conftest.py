import pytest
from typing import Tuple
from sklearn import linear_model  # type: ignore
import numpy as np
import pandas as pd
from opsml.model import SklearnModel, TaskType
from opsml.data import NumpyData, PandasData, SqlLogic
from opsml.helpers.data import create_fake_data
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # type: ignore
from sklearn import ensemble
from sklearn.compose import ColumnTransformer  # type: ignore
from sklearn.pipeline import Pipeline  # type: ignore
import lightgbm as lgb  # type: ignore
from sklearn.calibration import CalibratedClassifierCV  # type: ignore
import numpy as np
from xgboost import XGBRegressor
from sklearn import (
    cross_decomposition,
    ensemble,
    gaussian_process,
    linear_model,
    multioutput,
    naive_bayes,
    neighbors,
    neural_network,
    svm,
    tree,
)
from sklearn.feature_selection import SelectPercentile, chi2  # type: ignore
from sklearn.impute import SimpleImputer  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.datasets import fetch_openml, load_iris  # type: ignore


@pytest.fixture(scope="session")
def example_dataframe():
    X, y = create_fake_data(n_samples=1200)

    return X, y, X, y


@pytest.fixture
def regression_data() -> Tuple[np.ndarray, np.ndarray]:
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3

    X = X.astype(np.float32)
    y = y.astype(np.float32)

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


@pytest.fixture
def sklearn_pipeline() -> Tuple[SklearnModel, PandasData]:
    data = pd.DataFrame(
        [
            dict(CAT1="a", CAT2="c", num1=0.5, num2=0.6, num3=0, y=0),
            dict(CAT1="b", CAT2="d", num1=0.4, num2=0.8, num3=1, y=1),
            dict(CAT1="a", CAT2="d", num1=0.5, num2=0.56, num3=0, y=0),
            dict(CAT1="a", CAT2="d", num1=0.55, num2=0.56, num3=2, y=1),
            dict(CAT1="a", CAT2="c", num1=0.35, num2=0.86, num3=0, y=0),
            dict(CAT1="a", CAT2="c", num1=0.5, num2=0.68, num3=2, y=1),
        ]
    )
    cat_cols = ["CAT1", "CAT2"]
    train_data = data.drop("y", axis=1)
    categorical_transformer = Pipeline(
        [("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore"))]
    )
    preprocessor = ColumnTransformer(
        transformers=[("cat", categorical_transformer, cat_cols)],
        remainder="passthrough",
    )
    pipe = Pipeline(
        [
            ("preprocess", preprocessor),
            ("rf", lgb.LGBMRegressor(n_estimators=3, max_depth=3, num_leaves=5)),
        ]
    )
    pipe.fit(train_data, data["y"])
    sql_logic = SqlLogic(queries={"test": "SELECT * FROM TEST_TABLE"})

    model = SklearnModel(
        model=pipe, sample_data=train_data, preprocessor=pipe.named_steps["preprocess"]
    )
    data_interface = PandasData(
        data=train_data, sql_logic=sql_logic, dependent_vars=["y"]
    )
    return model, data_interface


@pytest.fixture
def lgb_classifier_calibrated(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = lgb.LGBMClassifier(
        n_estimators=3,
        max_depth=3,
        num_leaves=5,
    )
    reg.fit(X_train.to_numpy(), y_train)

    calibrated_model = CalibratedClassifierCV(reg, method="isotonic", cv="prefit")
    calibrated_model.fit(X_test, y_test)

    return SklearnModel(model=calibrated_model, sample_data=X_test[:10])


@pytest.fixture
def sklearn_pipeline_advanced() -> SklearnModel:
    X, y = fetch_openml(
        "titanic", version=1, as_frame=True, return_X_y=True, parser="pandas"
    )

    numeric_features = ["age", "fare"]
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_features = ["embarked", "sex", "pclass"]
    categorical_transformer = Pipeline(
        steps=[
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ("selector", SelectPercentile(chi2, percentile=50)),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", linear_model.LogisticRegression(max_iter=5)),
        ]
    )

    X_train, _, y_train, _ = train_test_split(
        X[:1000], y[:1000], test_size=0.2, random_state=0
    )

    assert isinstance(X_train, pd.DataFrame)
    assert isinstance(y_train, pd.Series)

    features = [*numeric_features, *categorical_features]
    X_train = X_train[features]
    y_train = y_train.to_numpy().astype(np.int32)

    clf.fit(X_train, y_train)
    return SklearnModel(model=clf, sample_data=X_train[:100])


@pytest.fixture
def stacking_regressor(regression_data) -> SklearnModel:
    X, y = regression_data

    estimators = [
        ("lr", ensemble.RandomForestRegressor(n_estimators=5)),
        ("svr", XGBRegressor(n_estimators=3, max_depth=3)),
        (
            "reg",
            lgb.LGBMRegressor(
                n_estimators=3,
                max_depth=3,
                num_leaves=5,
                objective="quantile",
                alpha="0.5",
            ),
        ),
    ]
    reg = ensemble.StackingRegressor(
        estimators=estimators,
        final_estimator=ensemble.RandomForestRegressor(n_estimators=5, random_state=42),
        cv=2,
    )
    reg.fit(X, y)
    return SklearnModel(model=reg, sample_data=X)
