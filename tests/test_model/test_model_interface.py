from sklearn.linear_model import LinearRegression

from opsml.registry.model.interfaces.sklearn import SklearnModel


def test_sklearn_interface(regression_data):
    X, y = regression_data
    reg = LinearRegression().fit(X, y)

    SklearnModel(model=reg, sample_data=X)
