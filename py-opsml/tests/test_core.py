from opsml.model import (
    HuggingFaceORTModel,
    HuggingFaceOnnxArgs,
    Feature,
    OnnxSchema,
    FeatureSchema,
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

    with pytest.raises(RuntimeError) as error:
        args = HuggingFaceOnnxArgs(
            ort_type=HuggingFaceORTModel.OrtAudioClassification,
            provider="CPUExecutionProvider",
            quantize=True,
            config="fail",
        )

    assert (
        str(error.value)
        == "Config must be an instance of AutoQuantizationConfig, ORTConfig, or QuantizationConfig"
    )

    args = HuggingFaceOnnxArgs(
        ort_type=HuggingFaceORTModel.OrtAudioClassification,
        provider="CPUExecutionProvider",
        quantize=True,
        config=AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False),
    )


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
    input_features = FeatureSchema(
        {"input1": Feature("type1", [1, 2, 3], {"arg1": "value1"})}
    )
    output_features = FeatureSchema(
        {"output1": Feature("type2", [4, 5, 6], {"arg2": "value2"})}
    )
    onnx_version = "1.0"

    schema = OnnxSchema(input_features, output_features, onnx_version)

    assert schema.input_features == input_features
    assert schema.output_features == output_features
    assert schema.onnx_version == onnx_version


def test_data_schema_creation():
    input_features = FeatureSchema(
        {"input1": Feature("type1", [1, 2, 3], {"arg1": "value1"})}
    )
    output_features = FeatureSchema(
        {"output1": Feature("type2", [4, 5, 6], {"arg2": "value2"})}
    )
    OnnxSchema(input_features, output_features, "1.0")
