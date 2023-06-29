"""Tests large models and data.

These tests should be ran manually when you want to verify large data and model
registration works.
"""
import numpy as np
import pandas as pd
import pytest
import transformers

from opsml.registry import DataCard, ModelCard, CardRegistries


@pytest.mark.large
def test_register_large_data(api_registries: CardRegistries):
    # create a numpy 1d-array
    x = np.random.rand(500000, 100)

    # create data card
    registry = api_registries.data

    data_card = DataCard(
        data=x,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )
    registry.register_card(card=data_card)

    loaded_card: DataCard = registry.load_card(uid=data_card.uid)
    loaded_card.load_data()

    assert (loaded_card.data == x).all()
    assert loaded_card.data.shape == x.shape


@pytest.mark.large
def test_register_large_model(api_registries: CardRegistries) -> None:
    """An example of saving a large, pretrained model to opsml"""
    model = transformers.WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
    model.config.forced_decoder_ids = None

    # come up with some dummy test data to fake out training.
    data = pd.DataFrame({"test": [1.0] * 80})

    data_card = DataCard(
        data=data[0:1].to_numpy(),
        name="dummy-data",
        team="mlops",
        user_email="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1].to_numpy(),
        name="whisper-small",
        team="mlops",
        user_email="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
        to_onnx=False,  # onnx conversion fails w/ this model - not sure why
    )
    api_registries.model.register_card(model_card)
