import pytest
from typing import Tuple, Any, Generator, cast
from sklearn import linear_model  # type: ignore
import numpy as np
import pandas as pd
from opsml.model import SklearnModel, TaskType, LightningModel
from opsml.data import NumpyData, PandasData, SqlLogic
from opsml.helpers.data import create_fake_data
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # type: ignore
from sklearn import ensemble
from sklearn.compose import ColumnTransformer  # type: ignore
from sklearn.pipeline import Pipeline  # type: ignore
import lightgbm as lgb  # type: ignore
from sklearn.calibration import CalibratedClassifierCV  # type: ignore
from xgboost import XGBRegressor, XGBClassifier  # type: ignore
from sklearn import (
    cross_decomposition,
    gaussian_process,
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
from sklearn.datasets import load_iris  # type: ignore
import xgboost as xgb  # type: ignore
import torch
from torch import nn
from torch.nn import MSELoss
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset, TensorDataset
import lightning as L  # type: ignore
import shutil
from transformers import pipeline, BartModel, BartTokenizer, TFBartModel  # type: ignore
from PIL import Image
from transformers import ViTFeatureExtractor, ViTForImageClassification
from opsml.data import TorchData
from catboost import CatBoostClassifier, CatBoostRanker, CatBoostRegressor, Pool  # type: ignore
from opsml.data import ColType, ColumnSplit, DataSplit


def cleanup() -> None:
    """Removes temp files"""

    # delete lightning_logs
    shutil.rmtree("lightning_logs", ignore_errors=True)


@pytest.fixture(scope="session")
def example_dataframe() -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

    return X, y, X, y


@pytest.fixture(scope="module")
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

    calibrated_model = CalibratedClassifierCV(reg, method="isotonic", cv=2)
    calibrated_model.fit(X_test, y_test)

    return SklearnModel(model=calibrated_model, sample_data=X_test[:10])


@pytest.fixture
def sklearn_pipeline_advanced() -> SklearnModel:
    X = pd.read_csv("tests/assets/titanic.csv")

    y = X.pop("survived")

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


@pytest.fixture
def sklearn_pipeline_xgb_classifier():
    data = load_iris()
    X = data.data[:, :2]
    y = data.target

    ind = np.arange(X.shape[0])
    np.random.shuffle(ind)
    X = X[ind, :].copy().astype(np.float32)
    y = y[ind].copy()

    pipe = Pipeline(
        [("scaler", StandardScaler()), ("xgb", XGBClassifier(n_estimators=3))]
    )
    pipe.fit(X, y)

    return SklearnModel(model=pipe, sample_data=X)


@pytest.fixture
def stacking_classifier():
    from sklearn.datasets import load_iris
    from sklearn.pipeline import make_pipeline

    X, y = load_iris(return_X_y=True)
    estimators = [
        ("rf", ensemble.RandomForestClassifier(n_estimators=10, random_state=42)),
        (
            "svr",
            make_pipeline(
                StandardScaler(), linear_model.LogisticRegression(max_iter=5)
            ),
        ),
    ]
    reg = ensemble.StackingClassifier(
        estimators=estimators,
        final_estimator=linear_model.LogisticRegression(max_iter=5),
    )
    reg.fit(X, y.astype(np.int32))
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def lgb_classifier_calibrated_pipeline(example_dataframe):
    X_train, y_train, X_test, y_test = example_dataframe
    reg = lgb.LGBMClassifier(
        n_estimators=3,
        max_depth=3,
        num_leaves=5,
    )

    pipe = Pipeline(
        [
            ("preprocess", StandardScaler()),
            ("clf", CalibratedClassifierCV(reg, method="isotonic", cv=3)),
        ]
    )
    pipe.fit(X_train, y_train)

    return SklearnModel(model=pipe, sample_data=X_test[:10])


@pytest.fixture
def ard_regression(regression_data) -> SklearnModel:
    X, y = regression_data
    reg = linear_model.ARDRegression().fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture(scope="module")
def classification_data():
    from sklearn.datasets import make_classification

    X, y = make_classification(
        n_samples=1000,
        n_features=4,
        n_informative=2,
        n_redundant=0,
        random_state=0,
        shuffle=False,
    )
    return X.astype(np.float32), y.astype(np.int32)


@pytest.fixture
def ada_boost_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.AdaBoostClassifier(n_estimators=5, random_state=0)
    clf.fit(X, y)
    return SklearnModel(model=clf, sample_data=X)


@pytest.fixture
def ada_regression(regression_data):
    X, y = regression_data
    reg = ensemble.AdaBoostRegressor(n_estimators=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def bagging_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.BaggingClassifier(n_estimators=5)
    clf.fit(X, y)
    return SklearnModel(model=clf, sample_data=X)


@pytest.fixture
def bagging_regression(regression_data):
    X, y = regression_data
    reg = ensemble.BaggingRegressor(n_estimators=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def bayesian_ridge_regression(regression_data):
    X, y = regression_data
    reg = linear_model.BayesianRidge(max_iter=10).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def bernoulli_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.BernoulliNB(force_alpha=True).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def categorical_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.CategoricalNB(force_alpha=True).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def complement_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.ComplementNB(force_alpha=True).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def decision_tree_regressor(regression_data):
    X, y = regression_data
    reg = tree.DecisionTreeRegressor(max_depth=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def decision_tree_classifier(classification_data):
    X, y = classification_data

    # make X int
    X = X.astype(np.int64)

    clf = tree.DecisionTreeClassifier(max_depth=5).fit(X, y)
    clf.fit(X, y)
    return SklearnModel(model=clf, sample_data=X)


@pytest.fixture
def elastic_net(regression_data):
    X, y = regression_data
    reg = linear_model.ElasticNet(max_iter=10).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def elastic_net_cv(regression_data):
    X, y = regression_data
    reg = linear_model.ElasticNetCV(max_iter=10, cv=2).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def extra_tree_regressor(regression_data):
    X, y = regression_data
    reg = tree.ExtraTreeRegressor(max_depth=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def extra_trees_regressor(regression_data):
    X, y = regression_data
    reg = ensemble.ExtraTreesRegressor(n_estimators=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def extra_tree_classifier(classification_data):
    X, y = classification_data
    clf = tree.ExtraTreeClassifier(max_depth=5).fit(X, y)
    clf.fit(X, y)
    return SklearnModel(model=clf, sample_data=X)


@pytest.fixture
def extra_trees_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.ExtraTreesClassifier(n_estimators=5).fit(X, y)
    clf.fit(X, y)
    return SklearnModel(model=clf, sample_data=X)


@pytest.fixture
def gamma_regressor(regression_data):
    X, y = regression_data
    reg = linear_model.GammaRegressor(max_iter=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def gaussian_nb(regression_data):
    X, y = regression_data
    reg = naive_bayes.GaussianNB().fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def gaussian_process_regressor(regression_data):
    X, y = regression_data
    reg = gaussian_process.GaussianProcessRegressor().fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def gradient_booster_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.GradientBoostingClassifier(n_estimators=5)
    clf.fit(X, y)
    return SklearnModel(model=clf, sample_data=X)


@pytest.fixture
def gradient_booster_regressor(regression_data):
    X, y = regression_data
    reg = ensemble.GradientBoostingRegressor(n_estimators=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def hist_booster_classifier(classification_data):
    X, y = classification_data
    clf = ensemble.HistGradientBoostingClassifier(max_iter=5)
    clf.fit(X, y)
    return SklearnModel(model=clf, sample_data=X)


@pytest.fixture
def hist_booster_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = ensemble.HistGradientBoostingRegressor(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def huber_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.HuberRegressor(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def knn_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = neighbors.KNeighborsRegressor(n_neighbors=2).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def knn_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf = neighbors.KNeighborsClassifier(n_neighbors=2).fit(X_train, y_train)
    return SklearnModel(model=clf, sample_data=X_train)


@pytest.fixture
def lars_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Lars().fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def lars_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LarsCV(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def lasso_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Lasso().fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def lasso_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoCV(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def lasso_lars_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoLars().fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def lasso_lars_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoLarsCV(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def lasso_lars_ic_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LassoLarsIC().fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def linear_svc(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.LinearSVC(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def linear_svr(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.LinearSVR(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def logistic_regression_cv(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.LogisticRegressionCV(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def mlp_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = neural_network.MLPClassifier(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def mlp_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = neural_network.MLPRegressor(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def multioutput_classification():
    from sklearn.datasets import make_multilabel_classification

    X, y = make_multilabel_classification(n_classes=3, random_state=0)
    reg = multioutput.MultiOutputClassifier(linear_model.LogisticRegression()).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multioutput_regression():
    from sklearn.datasets import load_linnerud

    X, y = load_linnerud(return_X_y=True)
    reg = multioutput.MultiOutputRegressor(linear_model.Ridge(random_state=123)).fit(
        X, y
    )
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multitask_elasticnet():
    X = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    y = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    reg = linear_model.MultiTaskElasticNet(alpha=0.1).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multitask_elasticnet_cv():
    X = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    y = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    reg = linear_model.MultiTaskElasticNetCV(max_iter=5, cv=2).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multitask_lasso():
    X = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    y = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    reg = linear_model.MultiTaskLasso(alpha=0.1).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multitask_lasso_cv():
    X = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    y = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    reg = linear_model.MultiTaskLassoCV(max_iter=5, cv=2).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multinomial_nb():
    X = np.array([[0, 0], [1, 1], [2, 2]]).astype(np.int64)
    y = np.array([1, 2, 3]).astype(np.int64)
    reg = naive_bayes.MultinomialNB().fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def nu_svc(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.NuSVC(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def nu_svr(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.NuSVR(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def pls_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = cross_decomposition.PLSRegression(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def passive_aggressive_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.PassiveAggressiveClassifier(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def passive_aggressive_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.PassiveAggressiveRegressor(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def perceptron(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Perceptron(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def poisson_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.PoissonRegressor(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def quantile_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.QuantileRegressor(solver="highs").fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def ransac_regressor():
    from sklearn import datasets

    n_samples = 1000
    n_outliers = 50

    X, y, _ = datasets.make_regression(
        n_samples=n_samples,
        n_features=1,
        n_informative=1,
        noise=10,
        coef=True,
        random_state=0,
    )
    np.random.seed(0)
    X[:n_outliers] = 3 + 0.5 * np.random.normal(size=(n_outliers, 1))
    y[:n_outliers] = -3 + 10 * np.random.normal(size=n_outliers)

    # X_train, y_train, _, _ = example_dataframe
    reg = linear_model.RANSACRegressor(max_trials=5).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def radius_neighbors_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = neighbors.RadiusNeighborsRegressor().fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def radius_neighbors_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf = neighbors.RadiusNeighborsClassifier().fit(X_train, y_train)
    return SklearnModel(model=clf, sample_data=X_train)


@pytest.fixture
def ridge_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.Ridge().fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def ridge_cv_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.RidgeCV(cv=2).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def ridge_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.RidgeClassifier(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def ridge_cv_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = linear_model.RidgeClassifierCV(cv=2).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def sgd_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.SGDClassifier(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def sgd_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.SGDRegressor(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def svc(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.SVC(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def svr(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = svm.SVR(max_iter=10).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def theilsen_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.TheilSenRegressor(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def tweedie_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    reg = reg = linear_model.TweedieRegressor(max_iter=5).fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def voting_classifier(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf1 = linear_model.LogisticRegression(max_iter=5)
    clf2 = ensemble.RandomForestClassifier(n_estimators=5, random_state=1)
    clf3 = naive_bayes.GaussianNB()
    eclf1 = ensemble.VotingClassifier(
        estimators=[("lr", clf1), ("rf", clf2), ("gnb", clf3)],
        voting="hard",
        flatten_transform=False,
    )
    reg = eclf1.fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def voting_regressor(example_dataframe):
    X_train, y_train, _, _ = example_dataframe
    clf1 = linear_model.LinearRegression()
    clf2 = ensemble.RandomForestRegressor(n_estimators=5, random_state=1)
    clf3 = linear_model.Lasso()
    eclf1 = ensemble.VotingRegressor(
        estimators=[("lr", clf1), ("rf", clf2), ("lso", clf3)]
    )
    reg = eclf1.fit(X_train, y_train)
    return SklearnModel(model=reg, sample_data=X_train)


@pytest.fixture
def lgb_booster_model(example_dataframe) -> Tuple[lgb.Booster, pd.DataFrame]:
    X_train, y_train, X_test, y_test = example_dataframe
    # create dataset for lightgbm
    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)
    # specify your configurations as a dict
    params = {
        "boosting_type": "gbdt",
        "objective": "regression",
        "metric": {"l2", "l1"},
        "num_leaves": 31,
        "learning_rate": 0.05,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": 0,
    }
    # train
    gbm = lgb.train(
        params,
        lgb_train,
        num_boost_round=20,
        valid_sets=[lgb_eval],
        callbacks=[
            lgb.early_stopping(stopping_rounds=5),
        ],
    )

    return gbm, X_train


@pytest.fixture
def xgb_booster_regressor_model(
    example_dataframe,
) -> Tuple[xgb.Booster, xgb.DMatrix, StandardScaler]:
    X_train, y_train, X_test, y_test = example_dataframe

    dtrain = xgb.DMatrix(X_train.to_numpy(), y_train.to_numpy())
    dtest = xgb.DMatrix(X_test.to_numpy(), y_test.to_numpy())

    param = {"max_depth": 2, "eta": 1, "objective": "reg:tweedie"}
    # specify validations set to watch performance
    watchlist = [(dtest, "eval"), (dtrain, "train")]

    # number of boosting rounds
    num_round = 2
    bst = xgb.train(param, dtrain, num_boost_round=num_round, evals=watchlist)

    return (bst, dtrain, StandardScaler())


@pytest.fixture(scope="module")
def pytorch_simple() -> Tuple[torch.nn.Module, dict]:
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
    inputs = {"x1": torch.randn((1, 1)), "x2": torch.randn((1, 1))}

    return (model, inputs)


@pytest.fixture(scope="module")
def pytorch_simple_tuple() -> Tuple[torch.nn.Module, tuple]:
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
    inputs = (torch.randn((1, 1)), torch.randn((1, 1)))

    return (model, inputs)


@pytest.fixture(scope="module")
def pytorch_lightning_model() -> Tuple[L.Trainer, torch.Tensor]:
    # define any number of nn.Modules (or use your current ones)
    nn.Sequential(nn.Linear(28 * 28, 64), nn.ReLU(), nn.Linear(64, 3))
    nn.Sequential(nn.Linear(3, 64), nn.ReLU(), nn.Linear(64, 28 * 28))

    # define the LightningModule
    class SimpleModel(L.LightningModule):
        def __init__(self):
            super().__init__()
            self.l1 = torch.nn.Linear(in_features=64, out_features=4)

        def forward(self, x):
            return torch.relu(self.l1(x.view(x.size(0), -1)))

    trainer = L.Trainer()
    model = SimpleModel()

    # set model
    trainer.strategy.model = model
    input_sample = torch.randn((1, 64))
    return (trainer, input_sample)


@pytest.fixture(scope="module")
def lightning_regression() -> Generator[Tuple[LightningModel, Any], None, None]:
    class SimpleDataset(Dataset):  # type: ignore
        def __init__(self) -> None:
            X = np.arange(10000)
            y = X * 2
            X = [[_] for _ in X]  # type: ignore
            y = [[_] for _ in y]  # type: ignore
            self.X = torch.Tensor(X)
            self.y = torch.Tensor(y)

        def __len__(self) -> int:
            return len(self.y)

        def __getitem__(self, idx: Any) -> Any:
            return {"X": self.X[idx], "y": self.y[idx]}

    class MyModel(L.LightningModule):
        def __init__(self) -> None:
            super().__init__()
            self.fc = nn.Linear(1, 1)
            self.criterion = MSELoss()

        def forward(self, inputs_id, labels=None) -> Any:
            outputs = self.fc(inputs_id)
            return outputs

        def train_dataloader(self) -> Any:
            dataset = SimpleDataset()
            return DataLoader(dataset, batch_size=1000)

        def training_step(self, batch, batch_idx) -> Any:
            input_ids = batch["X"]
            labels = batch["y"]
            outputs = self(input_ids, labels)
            loss = 0
            if labels is not None:
                loss = self.criterion(outputs, labels)
            return {"loss": loss}

        def configure_optimizers(self) -> Any:
            optimizer = Adam(self.parameters())
            return optimizer

    model = MyModel()
    trainer = L.Trainer(max_epochs=1)
    trainer.fit(model)

    X = torch.Tensor([[1.0], [51.0], [89.0]])

    yield (
        LightningModel(trainer=trainer, sample_data=X, preprocessor=StandardScaler()),
        MyModel,
    )
    cleanup()


@pytest.fixture(scope="module")
def lightning_classification() -> Generator[Tuple[LightningModel, Any], None, None]:
    class BinaryClassifier(L.LightningModule):
        def __init__(self):
            super().__init__()
            self.model = nn.Sequential(
                nn.Linear(5, 10), nn.ReLU(), nn.Linear(10, 1), nn.Sigmoid()
            )

        def forward(self, x):
            return self.model(x)

        def training_step(self, batch, batch_idx):
            x, y = batch
            y_hat = self(x).squeeze()
            loss = nn.functional.binary_cross_entropy(y_hat, y)
            return loss

        def configure_optimizers(self):
            return torch.optim.Adam(self.parameters(), lr=0.01)

    # Create sample data
    X = torch.randn(100, 5)
    y = torch.randint(0, 2, (100,), dtype=torch.float32)
    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Train the model
    model = BinaryClassifier()
    trainer = L.Trainer(max_epochs=1)
    trainer.fit(model, dataloader)

    yield (
        LightningModel(trainer=trainer, sample_data=X),
        BinaryClassifier,
    )
    cleanup()


@pytest.fixture(scope="module")
def huggingface_text_classification_pipeline() -> Generator[
    Tuple[Pipeline, str], None, None
]:
    pipe = pipeline("text-classification")
    data = "This restaurant is awesome"

    yield (pipe, data)


@pytest.fixture(scope="module")
def huggingface_bart_model() -> Generator[
    Tuple[BartModel, BartTokenizer, torch.Tensor], None, None
]:
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
    model = BartModel.from_pretrained("facebook/bart-base")
    inputs = tokenizer(["Hello. How are you"], return_tensors="pt")

    yield (model, tokenizer, inputs)


@pytest.fixture(scope="module")
def huggingface_tf_bart_model() -> Generator[
    Tuple[TFBartModel, BartTokenizer, torch.Tensor], None, None
]:
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
    model = TFBartModel.from_pretrained("facebook/bart-base")
    inputs = tokenizer(["Hello. How are you"], return_tensors="pt")

    yield (model, tokenizer, inputs)


@pytest.fixture(scope="module")
def huggingface_vit() -> Generator[
    Tuple[ViTForImageClassification, ViTFeatureExtractor, TorchData], None, None
]:
    image = Image.open("tests/assets/cats.jpg")

    feature_extractor = ViTFeatureExtractor.from_pretrained(
        "google/vit-base-patch16-224-in21k"
    )
    model = ViTForImageClassification.from_pretrained(
        "google/vit-base-patch16-224-in21k"
    )

    inputs = feature_extractor(images=image, return_tensors="pt")

    data = TorchData(data=inputs["pixel_values"])

    yield (model, feature_extractor, data)


@pytest.fixture
def catboost_regressor(
    example_dataframe: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame],
) -> Generator[Tuple[CatBoostRegressor, pd.DataFrame], None, None]:
    X_train, y_train, X_test, y_test = example_dataframe

    reg = CatBoostRegressor(n_estimators=5, max_depth=3)
    reg.fit(X_train.to_numpy(), y_train)

    yield (reg, X_train)


@pytest.fixture
def catboost_classifier(
    example_dataframe: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame],
) -> Generator[Tuple[CatBoostClassifier, pd.DataFrame], None, None]:
    X_train, y_train, X_test, y_test = example_dataframe

    reg = CatBoostClassifier(n_estimators=5, max_depth=3)
    reg.fit(X_train.to_numpy(), y_train)

    yield (reg, X_train)


@pytest.fixture
def catboost_ranker() -> Generator[Tuple[CatBoostRanker, pd.DataFrame], None, None]:
    from catboost.datasets import msrank_10k  # type: ignore

    train_df, _ = msrank_10k()

    X_train = train_df.drop([0, 1], axis=1).values
    y_train = train_df[0].values
    queries_train = train_df[1].values

    max_relevance = np.max(y_train)
    y_train /= max_relevance

    train = Pool(
        data=X_train[:1000], label=y_train[:1000], group_id=queries_train[:1000]
    )

    parameters = {
        "iterations": 100,
        "custom_metric": ["PrecisionAt:top=10", "RecallAt:top=10", "MAP:top=10"],
        "loss_function": "RMSE",
        "verbose": False,
        "random_seed": 0,
    }

    model = CatBoostRanker(**parameters)
    model.fit(train)

    yield (model, X_train)


@pytest.fixture
def lightgbm_regression(regression_data) -> SklearnModel:
    X, y = regression_data
    reg = lgb.LGBMRegressor().fit(X, y)
    return SklearnModel(
        model=reg,
        sample_data=X,
        task_type=TaskType.Regression,
    )


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
