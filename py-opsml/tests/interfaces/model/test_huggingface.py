from opsml.model import (
    HuggingFaceTask,
    HuggingFaceModel,
    HuggingFaceOnnxArgs,
    HuggingFaceORTModel,
    ModelSaveKwargs,
    ModelLoadKwargs,
)
from pathlib import Path
from typing import Tuple
import torch
from transformers import Pipeline, BartModel, BartTokenizer, TFBartModel  # type: ignore
from optimum.onnxruntime.configuration import AutoQuantizationConfig  # type: ignore
import pytest
from tests.conftest import EXCLUDE
from transformers import ViTFeatureExtractor, ViTForImageClassification
from opsml.data import TorchData


@pytest.mark.skipif(EXCLUDE, reason="Test not supported")
def test_hugging_face_text_pipeline(
    tmp_path: Path,
    huggingface_text_classification_pipeline: Tuple[Pipeline, str],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    pipe, data = huggingface_text_classification_pipeline
    interface = HuggingFaceModel(
        model=pipe,
        hf_task=HuggingFaceTask.TextClassification,
        sample_data=data,
    )

    onnx_args = HuggingFaceOnnxArgs(
        ort_type=HuggingFaceORTModel.OrtSequenceClassification,
        provider="CPUExecutionProvider",
        quantize=True,
        config=AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False),
    )

    kwargs = ModelSaveKwargs(onnx=onnx_args)

    metadata = interface.save(save_path, save_kwargs=kwargs)

    assert interface.onnx_session is not None

    interface.onnx_session.session = None
    assert interface.onnx_session.session is None

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.onnx_session is not None


@pytest.mark.skipif(EXCLUDE, reason="Test not supported")
def test_hugging_face_model(
    tmp_path: Path,
    huggingface_bart_model: Tuple[BartModel, BartTokenizer, torch.Tensor],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, tokenizer, data = huggingface_bart_model

    interface = HuggingFaceModel(
        model=model,
        tokenizer=tokenizer,
        hf_task=HuggingFaceTask.FeatureExtraction,
        sample_data=data,
    )

    onnx_args = HuggingFaceOnnxArgs(
        ort_type=HuggingFaceORTModel.OrtFeatureExtraction,
        provider="CPUExecutionProvider",
    )

    kwargs = ModelSaveKwargs(onnx=onnx_args)
    metadata = interface.save(save_path, save_kwargs=kwargs)
    assert interface.onnx_session is not None

    interface.onnx_session.session = None
    assert interface.onnx_session.session is None

    interface.tokenizer = None
    assert interface.tokenizer is None

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.onnx_session is not None
    assert interface.tokenizer is not None


@pytest.mark.tensorflow
@pytest.mark.skipif((EXCLUDE), reason="Test not supported")
def test_hugging_face_tf_model(
    tmp_path: Path,
    huggingface_tf_bart_model: Tuple[TFBartModel, BartTokenizer, torch.Tensor],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, tokenizer, data = huggingface_tf_bart_model

    interface = HuggingFaceModel(
        model=model,
        tokenizer=tokenizer,
        hf_task=HuggingFaceTask.FeatureExtraction,
        sample_data=data,
    )

    metadata = interface.save(save_path)

    interface.tokenizer = None
    assert interface.tokenizer is None

    interface.load(save_path, metadata.save_metadata)

    assert interface.tokenizer is not None


@pytest.mark.skipif(EXCLUDE, reason="Test not supported")
def test_huggingface_vit(
    tmp_path: Path,
    huggingface_vit: Tuple[ViTForImageClassification, ViTFeatureExtractor, TorchData],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, feature_extractor, inputs = huggingface_vit

    interface = HuggingFaceModel(
        model=model,
        image_processor=feature_extractor,
        sample_data=inputs,
        hf_task=HuggingFaceTask.ImageClassification,
    )

    interface.save(save_path)
