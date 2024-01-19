"""Tests large models and data.

These tests should be ran manually when you want to verify large data and model
registration works.
"""

from typing import Tuple

import numpy as np
import pytest

from opsml.cards import DataCard, ModelCard
from opsml.data import NumpyData, TorchData
from opsml.model import HuggingFaceModel
from opsml.registry import CardRegistries


@pytest.mark.large
def test_register_large_data(api_registries: CardRegistries):

    data = NumpyData(data=np.random.rand(500000, 100))

    # create data card
    registry = api_registries.data

    data_card = DataCard(
        interface=data,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
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
        repository="mlops",
        contact="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        interface=model,
        name="whisper-small",
        repository="mlops",
        contact="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
    )
    api_registries.model.register_card(model_card)
    assert model_card.metadata.data_schema.output_features["outputs"].shape == (1, 26)


@pytest.mark.large
def test_register_large_gpt_model(api_registries: CardRegistries, huggingface_openai_gpt: HuggingFaceModel) -> None:
    """An example of saving a large, pretrained gpt model to opsml"""
    model, data = huggingface_openai_gpt

    data_card = DataCard(
        interface=data,
        name="dummy-data",
        repository="mlops",
        contact="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        interface=model,
        name="gpt",
        repository="mlops",
        contact="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
    )
    api_registries.model.register_card(model_card)
    assert model_card.metadata.data_schema.output_features["logits"].shape == (1, 6, 40478)


@pytest.mark.large
def test_register_large_bart_model(
    api_registries: CardRegistries,
    huggingface_bart: HuggingFaceModel,
) -> None:
    """An example of saving a large, pretrained  bart model to opsml"""

    data = TorchData(data=huggingface_bart.sample_data["input_ids"])
    model = huggingface_bart

    data_card = DataCard(
        interface=data,
        name="dummy-data",
        repository="mlops",
        contact="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        interface=model,
        name="bart",
        repository="mlops",
        contact="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    api_registries.model.register_card(model_card)
    assert model_card.metadata.data_schema.output_features["last_hidden_state"].shape == (1, 7, 768)


@pytest.mark.large
def test_register_large_vit_model(
    api_registries: CardRegistries,
    huggingface_vit: Tuple[HuggingFaceModel, TorchData],
) -> None:
    """An example of saving a large, pretrained image model to opsml"""
    model, data = huggingface_vit

    data_card = DataCard(
        interface=data,
        name="dummy-data",
        repository="mlops",
        contact="test@mlops.com",
    )
    api_registries.data.register_card(data_card)

    model_card = ModelCard(
        interface=model,
        name="vit",
        repository="mlops",
        contact="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    api_registries.model.register_card(model_card)
    assert model_card.metadata.data_schema.output_features["logits"].shape == (1, 2)
