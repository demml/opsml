from typing import Tuple
from opsml.model import SklearnModel, ModelSaveKwargs
from opsml.data import NumpyData, PandasData
import pytest
from pytest_lazyfixture import lazy_fixture  # type: ignore
import warnings
from pathlib import Path


def warn(*args, **kwargs):
    pass


warnings.warn = warn


def test_linear_regression_numpy(
    tmp_path: Path, linear_regression: Tuple[SklearnModel, NumpyData]
):
    model, _ = linear_regression
    model.save(tmp_path, ModelSaveKwargs(save_onnx=True))
    assert model.onnx_session is not None
    model.onnx_session.run({"X": model.sample_data.data}, None)  # type: ignore


def test_random_forest_classifier(
    tmp_path: Path, random_forest_classifier: SklearnModel
):
    model = random_forest_classifier
    model.save(tmp_path, ModelSaveKwargs(save_onnx=True))
    assert model.onnx_session is not None


def test_sklearn_pipeline(
    tmp_path: Path, sklearn_pipeline: Tuple[SklearnModel, PandasData]
):
    model, _ = sklearn_pipeline
    save_kwargs = ModelSaveKwargs(
        onnx={"target_opset": {"ai.onnx.ml": 3, "": 9}}, save_onnx=True
    )
    model.save(tmp_path, save_kwargs=save_kwargs)
    assert model.onnx_session is not None


def test_lgb_classifier_calibrated(
    tmp_path: Path, lgb_classifier_calibrated: SklearnModel
):
    model = lgb_classifier_calibrated
    save_kwargs = ModelSaveKwargs(
        onnx={
            "target_opset": {"ai.onnx.ml": 3, "": 9},
            "options": {
                "zipmap": False,
            },
        }
    )
    model.save(tmp_path, save_kwargs=save_kwargs)
    assert model.onnx_session is not None


def test_sklearn_pipeline_advanced(
    tmp_path: Path, sklearn_pipeline_advanced: SklearnModel
):
    model = sklearn_pipeline_advanced
    save_kwargs = ModelSaveKwargs(
        onnx={"target_opset": {"ai.onnx.ml": 3, "": 9}}, save_onnx=True
    )
    model.save(tmp_path, save_kwargs=save_kwargs)
    assert model.onnx_session is not None


def test_stacking_regressor(tmp_path: Path, stacking_regressor: SklearnModel):
    model = stacking_regressor
    save_kwargs = ModelSaveKwargs(onnx={"target_opset": {"ai.onnx.ml": 3, "": 9}})
    model.save(tmp_path, save_kwargs=save_kwargs)
    assert model.onnx_session is not None


def test_sklearn_pipeline_xgb_classifier(
    tmp_path: Path,
    sklearn_pipeline_xgb_classifier: SklearnModel,
):
    model = sklearn_pipeline_xgb_classifier
    save_kwargs = ModelSaveKwargs(
        onnx={
            "options": {"zipmap": False},
            "target_opset": {"ai.onnx.ml": 3, "": 9},
        }
    )
    model.save(tmp_path, save_kwargs=save_kwargs)


def test_stacking_classifier(tmp_path: Path, stacking_classifier: SklearnModel):
    model = stacking_classifier
    save_kwargs = ModelSaveKwargs(
        onnx={
            "options": {"zipmap": False},
        }
    )
    model.save(tmp_path, save_kwargs=save_kwargs)


def test_lgb_classifier_calibrated_pipeline(
    tmp_path: Path,
    lgb_classifier_calibrated_pipeline: SklearnModel,
):
    model = lgb_classifier_calibrated_pipeline
    save_kwargs = ModelSaveKwargs(
        onnx={
            "options": {"zipmap": False},
            "target_opset": {"ai.onnx.ml": 3, "": 9},
        },
        save_onnx=True,
    )
    model.save(tmp_path, save_kwargs=save_kwargs)


@pytest.mark.parametrize(
    "interface",
    [
        lazy_fixture("ard_regression"),
        # lazy_fixture("ada_boost_classifier"), no longer works with onnx conversion (missing algorithm)
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
def test_sklearn_models(tmp_path: Path, interface: SklearnModel):
    model = interface
    model.save(tmp_path, ModelSaveKwargs(save_onnx=True))
