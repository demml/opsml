from opsml.model import (
    HuggingFaceTask,
    HuggingFaceModel,
    HuggingFaceOnnxArgs,
    HuggingFaceORTModel,
    SaveKwargs,
)
from pathlib import Path
from typing import Tuple
from transformers import Pipeline  # type: ignore


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
    )

    kwargs = SaveKwargs(
        onnx=onnx_args,
    )
    interface.save(save_path, True, save_kwargs=kwargs)
    a
