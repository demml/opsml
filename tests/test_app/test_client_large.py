"""Tests large models and data.

These tests should be ran manually when you want to verify large data and model
registration works.
"""

from typing import Any, Dict, Tuple

import numpy as np
import pytest
import torch

from opsml.cards import DataCard, ModelCard
from opsml.data import NumpyData
from opsml.model import HuggingFaceModel
from opsml.registry import CardRegistries


@pytest.mark.large
def _test_register_large_data(api_registries: CardRegistries):

    data = NumpyData(data=np.random.rand(500000, 100))

    # create data card
    registry = api_registries.data

    data_card = DataCard(
        interface=data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )
    registry.register_card(card=data_card)

    loaded_card: DataCard = registry.load_card(uid=data_card.uid)
    loaded_card.load_data()

    assert (loaded_card.data == data.data).all()
    assert loaded_card.data.shape == data.data.shape


# test opsml storage client
@pytest.mark.large
def test_register_large_whisper_model(
    api_registries: CardRegistries,
    huggingface_whisper: Tuple[HuggingFaceModel, NumpyData],
) -> None:
    """An example of saving a large, pretrained seq2seq model to opsml.

    ### Note:
        Whisper is a seq2seq model. To convert it to onnx, it must first be traced with JIT
    """
    model, data = huggingface_whisper
    data_card = DataCard(
        interface=data,
        name="dummy-data",
        team="mlops",
        user_email="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        interface=model,
        name="whisper-small",
        team="mlops",
        user_email="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
    )
    api_registries.model.register_card(model_card)
    print(model_card.metadata.data_schema)
    a


@pytest.mark.large
def _test_register_large_gpt_model(
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
        to_onnx=True,
    )
    api_registries.model.register_card(model_card)


@pytest.mark.large
def _test_register_large_bart_model(
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
        to_onnx=True,
    )

    api_registries.model.register_card(model_card)


@pytest.mark.large
def _test_register_large_vit_model(
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
        to_onnx=True,
    )

    api_registries.model.register_card(model_card)
