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
from xgboost import XGBRegressor, XGBClassifier  # type: ignore
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
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskElasticNet(alpha=0.1).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multitask_elasticnet_cv():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskElasticNetCV(max_iter=5, cv=2).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multitask_lasso():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskLasso(alpha=0.1).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multitask_lasso_cv():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([[0, 0], [1, 1], [2, 2]])
    reg = linear_model.MultiTaskLassoCV(max_iter=5, cv=2).fit(X, y)
    return SklearnModel(model=reg, sample_data=X)


@pytest.fixture
def multinomial_nb():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([1, 2, 3])
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
    clf1 = linear_model.LogisticRegression(multi_class="multinomial", max_iter=5)
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
