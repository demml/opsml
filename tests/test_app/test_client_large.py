"""Tests large models and data.

These tests should be ran manually when you want to verify large data and model
registration works.
"""

from typing import Tuple, Any, Dict
import numpy as np
import pytest
import torch
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


# test opsml storage client
@pytest.mark.large
def test_register_large_whisper_model(
    api_registries: CardRegistries,
    huggingface_whisper: Tuple[Any, Dict[str, np.ndarray]],
) -> None:
    """An example of saving a large, pretrained seq2seq model to opsml.

    ### Note:
        Whisper is a seq2seq model. To convert it to onnx, it must first be traced with JIT
    """
    model, data = huggingface_whisper
    data_card = DataCard(
        data=data,
        name="dummy-data",
        team="mlops",
        user_email="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data,
        name="whisper-small",
        team="mlops",
        user_email="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
        to_onnx=False,  # seq2seq need to be handled differently
    )
    api_registries.model.register_card(model_card)
    assert model_card.metadata.data_schema.model_data_schema.output_features["outputs"].shape == [1, 26]


@pytest.mark.large
def test_register_large_gpt_model(
    api_registries: CardRegistries,
    huggingface_openai_gpt: Tuple[Any, Dict[str, torch.Tensor]],
) -> None:
    """An example of saving a large, pretrained gpt model to opsml"""
    model, data = huggingface_openai_gpt

    data_card = DataCard(
        data=data["input_ids"].numpy(),
        name="dummy-data",
        team="mlops",
        user_email="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data={"input_ids": data["input_ids"].numpy()},
        name="gpt",
        team="mlops",
        user_email="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
    )
    api_registries.model.register_card(model_card)


@pytest.mark.large
def test_register_large_bart_model(
    api_registries: CardRegistries,
    huggingface_bart: Tuple[Any, Dict[str, torch.Tensor]],
) -> None:
    """An example of saving a large, pretrained  bart model to opsml"""
    model, data = huggingface_bart

    data_card = DataCard(
        data=data["input_ids"].numpy(),
        name="dummy-data",
        team="mlops",
        user_email="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data={"input_ids": data["input_ids"].numpy()},
        name="bart",
        team="mlops",
        user_email="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
    )

    api_registries.model.register_card(model_card)


@pytest.mark.large
def test_register_large_vit_model(
    api_registries: CardRegistries,
    huggingface_vit: Tuple[Any, Dict[str, torch.Tensor]],
) -> None:
    """An example of saving a large, pretrained image model to opsml"""
    model, data = huggingface_vit

    data_card = DataCard(
        data=data["pixel_values"].numpy(),
        name="dummy-data",
        team="mlops",
        user_email="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data={"pixel_values": data["pixel_values"].numpy()},
        name="vit",
        team="mlops",
        user_email="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
        # to_onnx=False,  # onnx conversion fails w/ this model - not sure why
    )

    api_registries.model.register_card(model_card)
