from opsml.model import (
    HuggingFaceTask,
    HuggingFaceModel,
)
from pathlib import Path
from typing import Tuple
import torch
from transformers import Pipeline, BartModel, BartTokenizer  # type: ignore
import pytest
import sys


IS_312 = sys.version_info >= (3, 12)

LINUX_EXCLUDE = sys.platform.startswith("linux")
WINDOWS_EXCLUDE = sys.platform == "win32"
EXCLUDE = bool(LINUX_EXCLUDE or WINDOWS_EXCLUDE)


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

    metadata = interface.save(save_path)

    interface.load(save_path, metadata.save_metadata)


# only want to run this on macos
@pytest.mark.skipif(EXCLUDE, reason="Test not supported")
def _test_hugging_face_model(
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

    metadata = interface.save(save_path)
    # assert interface.onnx_session is not None

    interface.tokenizer = None
    assert interface.tokenizer is None

    interface.load(
        save_path,
        metadata.save_metadata,
    )

    assert interface.tokenizer is not None
