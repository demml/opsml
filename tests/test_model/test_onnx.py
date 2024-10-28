# type: ignore
import warnings

import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.model import (
    HuggingFaceModel,
    LightningModel,
    ModelInterface,
    TensorFlowModel,
    TorchModel,
)
from tests import conftest
from tests.conftest import EXCLUDE


# this is done to filter all the convergence and user warnings during testing
def warn(*args, **kwargs):
    pass


warnings.warn = warn


@pytest.mark.flaky(reruns=2, reruns_delay=2)
@pytest.mark.parametrize(
    "interface",
    [
        lazy_fixture("lgb_classifier_calibrated"),
        lazy_fixture("linear_regression_model"),  # linear regress with numpy
        lazy_fixture("random_forest_classifier"),  # random forest with dataframe
        lazy_fixture("xgb_df_regressor"),  # xgb with dataframe
        lazy_fixture("lgb_booster_model"),  # lgb base package with dataframe
        lazy_fixture("lgb_classifier"),  # lgb classifier with dataframe
        lazy_fixture("sklearn_pipeline_model"),  # sklearn pipeline with dict onnx input
        lazy_fixture("sklearn_pipeline_advanced"),  # nested pipelines
        lazy_fixture("stacking_regressor"),  # stacking regressor with lgb as one estimator
        ###### test all supported sklearn estimators
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
        lazy_fixture("stacking_classifier"),
        lazy_fixture("theilsen_regressor"),
        lazy_fixture("tweedie_regressor"),
        lazy_fixture("voting_classifier"),
        lazy_fixture("voting_regressor"),
        lazy_fixture("lgb_classifier_calibrated_pipeline"),
        lazy_fixture("catboost_regressor"),  # test catboost
        lazy_fixture("catboost_classifier"),  # test catboost
        lazy_fixture("catboost_ranker"),  # test catboost
    ],
)
def test_sklearn_models(interface: ModelInterface):
    interface.convert_to_onnx()
    assert interface.onnx_model.sess is not None


@pytest.mark.flaky(reruns=2)
@pytest.mark.skipif(EXCLUDE, reason="Not supported")
@pytest.mark.parametrize(
    "interface",
    [
        lazy_fixture("tf_transformer_example"),  # keras transformer example
        lazy_fixture("multi_input_tf_example"),  # keras multi input model
    ],
)
def test_tensorflow_predict(interface: TensorFlowModel):
    interface.convert_to_onnx()
    assert interface.onnx_model.sess is not None
