import sys

from opsml.registry.cards.cards import ModelCard
import numpy as np
import pytest
import pandas as pd
from pytest_lazyfixture import lazy_fixture
from opsml.model.types import ModelMetadata
import warnings


# this is done to filter all the convergence and user warnings during testing
def warn(*args, **kwargs):
    pass


warnings.warn = warn


def model_predict(model_and_data):
    model, data = model_and_data

    if isinstance(data, dict):
        sample_data = data
    else:
        sample_data = data[0:1]

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=sample_data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )
    predictor = model_card.onnx_model()

    if isinstance(data, np.ndarray):
        input_name = next(iter(predictor.data_schema.model_data_schema.input_features.keys()))

        record = {input_name: data[0, :].tolist()}

    elif isinstance(data, pd.DataFrame):
        record = list(sample_data[0:1].T.to_dict().values())[0]

    else:
        record = {}
        for feat, val in sample_data.items():
            record[feat] = np.ravel(val).tolist()

    pred_onnx = predictor.predict(record)

    out_sig = predictor.output_sig(**pred_onnx)
    pred_orig = predictor.predict_with_model(model, record)


@pytest.mark.parametrize(
    "model_and_data",
    [
        lazy_fixture("linear_regression"),  # linear regress with numpy
        lazy_fixture("random_forest_classifier"),  # random forest with dataframe
        lazy_fixture("xgb_df_regressor"),  # xgb with dataframe
        lazy_fixture("lgb_booster_dataframe"),  # lgb base package with dataframe
        lazy_fixture("lgb_classifier"),  # lgb classifier with dataframe
        lazy_fixture("sklearn_pipeline"),  # sklearn pipeline with dict onnx input
        lazy_fixture("sklearn_pipeline_advanced"),
        lazy_fixture("stacking_regressor"),  # stacking regressor with lgb as one estimator
        ## test all supported sklearn estimators
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
    ],
)
def test_sklearn_models(model_and_data):
    model_predict(model_and_data)


@pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on apple silicon")
@pytest.mark.parametrize(
    "model_and_data",
    [
        # Not supportd on apple silicon
        lazy_fixture("load_transformer_example"),  # keras transformer example
        lazy_fixture("load_multi_input_keras_example"),  # keras multi input model
        lazy_fixture("load_pytorch_resnet"),  # pytorch resent trained with numpy array
        lazy_fixture("load_pytorch_language"),  # huggingface automodel "distil-bert" trained with dictionary
    ],
)
def test_model_predict_linux_only(model_and_data):
    model_predict(model_and_data)


@pytest.mark.parametrize(
    "model_and_data",
    [
        lazy_fixture("linear_regression"),  # linear regress with numpy
    ],
)
def test_byo_onnx(model_and_data):
    model, data = model_and_data

    if isinstance(data, dict):
        sample_data = data
    else:
        sample_data = data[0:1]

    # create model def first
    modelcard = ModelCard(
        trained_model=model,
        sample_input_data=sample_data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )
    predictor = modelcard.onnx_model()
    model_def = modelcard.onnx_model_def

    # byo onnx model def
    new_modelcard = ModelCard(
        trained_model=model,
        sample_input_data=sample_data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
        onnx_model_def=model_def,
    )
    predictor = new_modelcard.onnx_model()
    assert new_modelcard.data_schema is not None

    if isinstance(data, np.ndarray):
        input_name = next(iter(predictor.data_schema.model_data_schema.input_features.keys()))

        record = {input_name: data[0, :].tolist()}

    elif isinstance(data, pd.DataFrame):
        record = list(sample_data[0:1].T.to_dict().values())[0]

    else:
        record = {}
        for feat, val in sample_data.items():
            record[feat] = np.ravel(val).tolist()

    pred_onnx = predictor.predict(record)

    out_sig = predictor.output_sig(**pred_onnx)
    pred_orig = predictor.predict_with_model(model, record)


@pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on apple silicon")
@pytest.mark.parametrize(
    "model_and_data",
    [
        lazy_fixture("pytorch_onnx_byo"),  # linear regress with numpy
    ],
)
def test_byo_pytorch_onnx(model_and_data):
    model_def, model, sample_data = model_and_data

    # create model def first
    modelcard = ModelCard(
        trained_model=model,
        sample_input_data=sample_data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
        onnx_model_def=model_def,
    )
    predictor = modelcard.onnx_model()
    input_name = next(iter(predictor.data_schema.model_data_schema.input_features.keys()))
    record = {input_name: sample_data[0, :].tolist()}
    pred_onnx = predictor.predict(record)
    pred_orig = predictor.predict_with_model(model, record)


# for random testing of definitions

# filename = "sklearn_pipeline"
#    with open(f"{filename}-v1-0-0.onnx", "wb") as file_:
#        file_.write(model_card.onnx_model_def.model_bytes)
#
#    model_def = ModelApiDef(
#        model_name=model_card.name,
#        model_type=model_card.model_type,
#        onnx_version=predictor.onnx_version,
#        model_version=predictor.model_version,
#        onnx_uri=f"{filename}-v1-0-0.onnx",
#        data_schema=predictor.data_schema,
#        sample_data=model_card._get_sample_data_for_api(),
#    )
#
#    import json
#
#    with open(f"{filename}_model_def.json", "w") as file_:
#        json.dump(model_def.dict(), file_)
