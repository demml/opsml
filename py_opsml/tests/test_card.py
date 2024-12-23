from opsml_core import (
    HuggingFaceORTModel,
    HuggingFaceOnnxArgs,
    OpsmlError,
    TorchOnnxArgs,
    Feature,
    OnnxSchema,
    DataSchema,
    Description,
    CardInfo,
)
from optimum.onnxruntime.configuration import AutoQuantizationConfig  # type: ignore
import pytest


@pytest.mark.parametrize(
    "variant",
    [
        HuggingFaceORTModel.OrtAudioClassification,
        HuggingFaceORTModel.OrtAudioFrameClassification,
        HuggingFaceORTModel.OrtAudioXVector,
        HuggingFaceORTModel.OrtCustomTasks,
        HuggingFaceORTModel.OrtCtc,
        HuggingFaceORTModel.OrtFeatureExtraction,
        HuggingFaceORTModel.OrtImageClassification,
        HuggingFaceORTModel.OrtMaskedLm,
        HuggingFaceORTModel.OrtMultipleChoice,
        HuggingFaceORTModel.OrtQuestionAnswering,
        HuggingFaceORTModel.OrtSemanticSegmentation,
        HuggingFaceORTModel.OrtSequenceClassification,
        HuggingFaceORTModel.OrtTokenClassification,
        HuggingFaceORTModel.OrtSeq2SeqLm,
        HuggingFaceORTModel.OrtSpeechSeq2Seq,
        HuggingFaceORTModel.OrtVision2Seq,
        HuggingFaceORTModel.OrtPix2Struct,
        HuggingFaceORTModel.OrtCausalLm,
        HuggingFaceORTModel.OrtOptimizer,
        HuggingFaceORTModel.OrtQuantizer,
        HuggingFaceORTModel.OrtTrainer,
        HuggingFaceORTModel.OrtSeq2SeqTrainer,
        HuggingFaceORTModel.OrtTrainingArguments,
        HuggingFaceORTModel.OrtSeq2SeqTrainingArguments,
        HuggingFaceORTModel.OrtStableDiffusionPipeline,
        HuggingFaceORTModel.OrtStableDiffusionImg2ImgPipeline,
        HuggingFaceORTModel.OrtStableDiffusionInpaintPipeline,
        HuggingFaceORTModel.OrtStableDiffusionXlPipeline,
        HuggingFaceORTModel.OrtStableDiffusionXlImg2ImgPipeline,
    ],
)
def test_huggingface_ort_model_variants(variant):
    assert variant is not None


def test_hugging_face_ort_model():
    args = HuggingFaceOnnxArgs(
        ort_type=HuggingFaceORTModel.OrtAudioClassification,
        provider="CPUExecutionProvider",
    )

    assert args.quantize is False

    args = HuggingFaceOnnxArgs(
        ort_type=HuggingFaceORTModel.OrtAudioClassification,
        provider="CPUExecutionProvider",
        quantize=True,
    )

    assert args.quantize is True

    with pytest.raises(OpsmlError) as error:
        args = HuggingFaceOnnxArgs(
            ort_type=HuggingFaceORTModel.OrtAudioClassification,
            provider="CPUExecutionProvider",
            quantize=True,
            config="fail",
        )

    assert (
        str(error.value)
        == "config must be an instance of AutoQuantizationConfig, ORTConfig, or QuantizationConfig"
    )

    args = HuggingFaceOnnxArgs(
        ort_type=HuggingFaceORTModel.OrtAudioClassification,
        provider="CPUExecutionProvider",
        quantize=True,
        config=AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False),
    )


def test_torch_onnx_args():
    args = TorchOnnxArgs(
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch"}},
        do_constant_folding=True,
        export_params=True,
        verbose=True,
    )

    assert args.do_constant_folding is True
    assert args.export_params is True

    # convert to dictionary
    args_dict = args.model_dump()

    assert args_dict == {
        "input_names": ["input"],
        "output_names": ["output"],
        "dynamic_axes": {"input": {0: "batch"}},
        "do_constant_folding": True,
        "export_params": True,
        "verbose": True,
    }


def test_feature_creation():
    feature_type = "example_type"
    shape = [1, 2, 3]
    extra_args = {"arg1": "value1", "arg2": "value2"}

    feature = Feature(feature_type, shape, extra_args)

    assert feature.feature_type == feature_type
    assert feature.shape == shape
    assert feature.extra_args == extra_args


def test_feature_default_extra_args():
    feature_type = "example_type"
    shape = [1, 2, 3]

    feature = Feature(feature_type, shape)

    assert feature.feature_type == feature_type
    assert feature.shape == shape
    assert feature.extra_args == {}


def test_onnx_schema_creation():
    input_features = {"input1": Feature("type1", [1, 2, 3], {"arg1": "value1"})}
    output_features = {"output1": Feature("type2", [4, 5, 6], {"arg2": "value2"})}
    onnx_version = "1.0"

    schema = OnnxSchema(input_features, output_features, onnx_version)

    assert schema.input_features == input_features
    assert schema.output_features == output_features
    assert schema.onnx_version == onnx_version


def test_data_schema_creation():
    data_type = "example_type"
    input_features = {"input1": Feature("type1", [1, 2, 3], {"arg1": "value1"})}
    output_features = {"output1": Feature("type2", [4, 5, 6], {"arg2": "value2"})}
    onnx_schema = OnnxSchema(input_features, output_features, "1.0")

    schema = DataSchema(data_type, input_features, output_features, onnx_schema)

    assert schema.data_type == data_type
    assert schema.input_features == input_features
    assert schema.output_features == output_features
    assert schema.onnx_schema == onnx_schema


def test_data_schema_default_values():
    data_type = "example_type"

    schema = DataSchema(data_type)

    assert schema.data_type == data_type
    assert schema.input_features is None
    assert schema.output_features is None
    assert schema.onnx_schema is None


def test_description_creation():
    summary = "This is a summary."
    sample_code = "print('Hello, world!')"
    notes = "These are some notes."

    description = Description(summary, sample_code, notes)

    assert description.summary == summary
    assert description.sample_code == sample_code
    assert description.notes == notes


def test_description_creation_markdown():
    summary = "assets/readme.md"
    sample_code = "print('Hello, world!')"
    notes = "These are some notes."

    description = Description(summary, sample_code, notes)

    assert description.summary != summary
    assert description.sample_code == sample_code
    assert description.notes == notes

    summary = "assets/no_readme.md"

    with pytest.raises(RuntimeError):
        description = Description(summary)


def test_card_info_initialization():
    card = CardInfo(
        name="Test Card",
        repository="https://github.com/test/repo",
        contact="test@example.com",
        uid="12345",
        version="1.0.0",
        tags={"key1": "value1", "key2": "value2"},
    )
    assert card.name == "Test Card"
    assert card.repository == "https://github.com/test/repo"
    assert card.contact == "test@example.com"
    assert card.uid == "12345"
    assert card.version == "1.0.0"
    assert card.tags == {"key1": "value1", "key2": "value2"}


def test_card_info_default_initialization():
    card = CardInfo()
    assert card.name is None
    assert card.repository is None
    assert card.contact is None
    assert card.uid is None
    assert card.version is None
    assert card.tags is None


def test_card_info_set_env():
    card = CardInfo(
        name="card",
        repository="repo",
        contact="user",
        uid="12345",
        version="1.0.0",
        tags={"key1": "value1", "key2": "value2"},
    )

    card.set_env()

    # this is only used for testing purposes because of the different env contexts between rust and python.
    # It works, but we don't necessarily want to expose this method to the user.
    # So we don't include the method in the .pyi class definition.
    set_vars = card.get_vars()

    assert set_vars["OPSML_RUNTIME_NAME"] == "card"
    assert set_vars["OPSML_RUNTIME_REPOSITORY"] == "repo"
    assert set_vars["OPSML_RUNTIME_CONTACT"] == "user"
