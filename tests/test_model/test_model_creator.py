from typing import Tuple

import pandas as pd
import pytest
from sklearn.base import BaseEstimator

from opsml.registry.cards import ModelCard
from opsml.registry.model.creator import ModelCreator, create_model
from opsml.registry.model.interfaces import (
    HuggingFaceModel,
    LightningModel,
    PyTorchModel,
    SklearnModel,
    TensorFlowModel,
)
from opsml.registry.types import AllowedDataType, ModelReturn


def _test_model_create_no_onnx(random_forest_classifier: Tuple[BaseEstimator, pd.DataFrame]):
    model: SklearnModel = random_forest_classifier
    modelcard = ModelCard(
        model=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )

    model_return = create_model(modelcard=modelcard)

def _test_tf_create_no_onnx(load_transformer_example: TensorFlowModel):
    
    modelcard = ModelCard(
        model=load_transformer_example,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )

    model_return: ModelReturn = create_model(modelcard=modelcard)
    assert model_return.data_schema.output_features["outputs"].shape == [1,2]
    
    
def _test_huggingface_no_onnx(huggingface_bart: HuggingFaceModel):
    model = huggingface_bart
    modelcard = ModelCard(
        model=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )

    model_return: ModelReturn = create_model(modelcard=modelcard)
    assert model_return.data_schema.output_features['last_hidden_state'].shape == (1, 7, 768)
    assert model_return.data_schema.input_features['input_ids'].shape == (1, 7)
    
def _test_huggingface_pipeline_no_onnx(huggingface_text_classification_pipeline: HuggingFaceModel):
    model = huggingface_text_classification_pipeline
    modelcard = ModelCard(
        model=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )

    model_return: ModelReturn = create_model(modelcard=modelcard)
    assert model_return.data_schema.output_features['score'].feature_type == "float"
    assert model_return.data_schema.input_features['input'].feature_type == "str"
    
    
def test_torch_no_onnx(deeplabv3_resnet50: PyTorchModel):
    model = deeplabv3_resnet50
    modelcard = ModelCard(
        model=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )

    model_return: ModelReturn = create_model(modelcard=modelcard)
    assert model_return.data_schema.output_features['out'].shape == (1, 21, 400, 400)
    assert model_return.data_schema.input_features['inputs'].shape == (1, 3, 400, 400)
   
def test_lightning_no_onnx(lightning_regression: LightningModel):
    model = lightning_regression
    modelcard = ModelCard(
        model=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )

    model_return: ModelReturn = create_model(modelcard=modelcard)
    assert model_return.data_schema.output_features['out'].shape == (1, 21, 400, 400)
    assert model_return.data_schema.input_features['inputs'].shape == (1, 3, 400, 400)
     
    
def _test_onnx_model_to_onnx(random_forest_classifier: Tuple[BaseEstimator, pd.DataFrame]):
    model: SklearnModel = random_forest_classifier
    modelcard = ModelCard(
        model=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
        to_onnx=True,
    )

    create_model(modelcard=modelcard)


def _test_model_creator(random_forest_classifier: Tuple[BaseEstimator, pd.DataFrame]):
    model, data = random_forest_classifier
    modelcard = ModelCard(
        trained_model=model,
        sample_input_data=data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
        to_onnx=True,
    )
    modelcard.trained_model = "Fail"
    modelcard.metadata.sample_data_type = AllowedDataType.PANDAS

    with pytest.raises(NotImplementedError):
        ModelCreator(modelcard=modelcard).create_model()

    with pytest.raises(NotImplementedError):
        ModelCreator.validate(True)
