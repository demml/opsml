from typing import Tuple
from opsml.core import OpsmlLogger, LogLevel
from opsml.model import SklearnModel
from opsml.data import NumpyData, PandasData
import pytest
from pytest_lazyfixture import lazy_fixture  # type: ignore
import warnings


def warn(*args, **kwargs):
    pass


warnings.warn = warn


OpsmlLogger.setup_logging(LogLevel.Debug)


def test_linear_regression_numpy(linear_regression: Tuple[SklearnModel, NumpyData]):
    model, _ = linear_regression
    model.convert_to_onnx()
    assert model.onnx_session is not None
    model.onnx_session.run({"X": model.sample_data.data}, None)  # type: ignore


def test_random_forest_classifier(random_forest_classifier: SklearnModel):
    model = random_forest_classifier
    model.convert_to_onnx()
    assert model.onnx_session is not None


def test_sklearn_pipeline(sklearn_pipeline: Tuple[SklearnModel, PandasData]):
    model, _ = sklearn_pipeline
    kwargs = {"target_opset": {"ai.onnx.ml": 3, "": 9}}
    model.convert_to_onnx(**kwargs)
    assert model.onnx_session is not None


def test_lgb_classifier_calibrated(lgb_classifier_calibrated: SklearnModel):
    model = lgb_classifier_calibrated
    kwargs = {
        "target_opset": {"ai.onnx.ml": 3, "": 9},
        "options": {
            "zipmap": False,
        },
    }
    model.convert_to_onnx(**kwargs)
    assert model.onnx_session is not None


@pytest.mark.flaky(reruns=2, reruns_delay=2)
def test_sklearn_pipeline_advanced(sklearn_pipeline_advanced: SklearnModel):
    model = sklearn_pipeline_advanced
    kwargs = {"target_opset": {"ai.onnx.ml": 3, "": 9}}
    model.convert_to_onnx(**kwargs)
    assert model.onnx_session is not None


def test_stacking_regressor(stacking_regressor: SklearnModel):
    model = stacking_regressor
    kwargs = {"target_opset": {"ai.onnx.ml": 3, "": 9}}
    model.convert_to_onnx(**kwargs)
    assert model.onnx_session is not None


def test_sklearn_pipeline_xgb_classifier(
    sklearn_pipeline_xgb_classifier: SklearnModel,
):
    model = sklearn_pipeline_xgb_classifier
    kwargs = {
        "options": {"zipmap": False},
        "target_opset": {"ai.onnx.ml": 3, "": 9},
    }
    model.convert_to_onnx(**kwargs)


def test_stacking_classifier(stacking_classifier: SklearnModel):
    model = stacking_classifier
    kwargs = {
        "options": {"zipmap": False},
    }
    model.convert_to_onnx(**kwargs)


def test_lgb_classifier_calibrated_pipeline(
    lgb_classifier_calibrated_pipeline: SklearnModel,
):
    model = lgb_classifier_calibrated_pipeline
    kwargs = {
        "options": {"zipmap": False},
        "target_opset": {"ai.onnx.ml": 3, "": 9},
    }
    model.convert_to_onnx(**kwargs)


@pytest.mark.parametrize(
    "interface",
    [
        lazy_fixture("ard_regression"),
        lazy_fixture("ada_boost_classifier"),
        lazy_fixture("ada_regression"),
        lazy_fixture("bagging_classifier"),
        lazy_fixture("bagging_regression"),
        lazy_fixture("bayesian_ridge_regression"),
        lazy_fixture("bernoulli_nb"),
        lazy_fixture("categorical_nb"),
        lazy_fixture("complement_nb"),
        lazy_fixture("decision_tree_regressor"),
        lazy_fixture("decision_tree_classifier"),
        lazy_fixture("elastic_net"),
        lazy_fixture("elastic_net_cv"),
        lazy_fixture("extra_tree_regressor"),
        lazy_fixture("extra_trees_regressor"),
        lazy_fixture("extra_tree_classifier"),
        lazy_fixture("extra_trees_classifier"),
        lazy_fixture("gamma_regressor"),
        lazy_fixture("gaussian_nb"),
        lazy_fixture("gaussian_process_regressor"),
        lazy_fixture("gradient_booster_classifier"),
        lazy_fixture("gradient_booster_regressor"),
        lazy_fixture("hist_booster_classifier"),
        lazy_fixture("hist_booster_regressor"),
        lazy_fixture("huber_regressor"),
        lazy_fixture("knn_regressor"),
        lazy_fixture("knn_classifier"),
        lazy_fixture("lars_regressor"),
        lazy_fixture("lars_cv_regressor"),
        lazy_fixture("lasso_regressor"),
        lazy_fixture("lasso_cv_regressor"),
        lazy_fixture("lasso_lars_regressor"),
        lazy_fixture("lasso_lars_cv_regressor"),
        lazy_fixture("lasso_lars_ic_regressor"),
        lazy_fixture("linear_svc"),
        lazy_fixture("linear_svr"),
        lazy_fixture("logistic_regression_cv"),
        lazy_fixture("mlp_classifier"),
        lazy_fixture("mlp_regressor"),
        lazy_fixture("multioutput_classification"),
        lazy_fixture("multioutput_regression"),
        lazy_fixture("multitask_elasticnet"),
        lazy_fixture("multitask_elasticnet_cv"),
        lazy_fixture("multitask_lasso"),
        lazy_fixture("multitask_lasso_cv"),
        lazy_fixture("multinomial_nb"),
        lazy_fixture("nu_svc"),
        lazy_fixture("nu_svr"),
        lazy_fixture("pls_regressor"),
        lazy_fixture("passive_aggressive_classifier"),
        lazy_fixture("passive_aggressive_regressor"),
        lazy_fixture("perceptron"),
        lazy_fixture("poisson_regressor"),
        lazy_fixture("quantile_regressor"),
        lazy_fixture("ransac_regressor"),
        lazy_fixture("radius_neighbors_regressor"),
        lazy_fixture("radius_neighbors_classifier"),
        lazy_fixture("ridge_regressor"),
        lazy_fixture("ridge_cv_regressor"),
        lazy_fixture("ridge_classifier"),
        lazy_fixture("ridge_cv_classifier"),
        lazy_fixture("sgd_classifier"),
        lazy_fixture("sgd_regressor"),
        lazy_fixture("svc"),
        lazy_fixture("svr"),
        lazy_fixture("theilsen_regressor"),
        lazy_fixture("tweedie_regressor"),
        lazy_fixture("voting_classifier"),
        lazy_fixture("voting_regressor"),
    ],
)
def test_sklearn_models(interface: SklearnModel):
    model = interface
    model.convert_to_onnx()
