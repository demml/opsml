from opsml.model.creator import OnnxModelCreator, ModelCreator
from opsml.registry.data.types import AllowedDataType
from opsml.registry.cards import ModelCard
import pandas as pd
import pytest
from sklearn.base import BaseEstimator
from typing import Tuple


def test_onnx_model_create_fail(random_forest_classifier: Tuple[BaseEstimator, pd.DataFrame]):
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

    with pytest.raises(Exception) as ve:
        OnnxModelCreator(modelcard=modelcard).create_model()

    assert ve.match("Failed to convert model to onnx format.")


def test_model_creator(random_forest_classifier: Tuple[BaseEstimator, pd.DataFrame]):
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
