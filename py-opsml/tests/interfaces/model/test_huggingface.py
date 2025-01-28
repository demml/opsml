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
from optimum.onnxruntime.configuration import AutoQuantizationConfig


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

    kwargs = SaveKwargs(
        onnx=onnx_args,
    )

    print(kwargs)
    metadata = interface.save(save_path, True, save_kwargs=kwargs)

    print(metadata)
    a
