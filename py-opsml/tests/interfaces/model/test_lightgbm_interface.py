from opsml.model import SklearnModel


def test_lgb_sklearn_api(lgb_model):
    model = lgb_model

    model = SklearnModel(model)
