from opsml_core import (
    CommonKwargs,
    SaveName,
    Suffix,
    OpsmlConfig,
    VersionType,
    RegistryType,
)
import pytest


@pytest.mark.parametrize(
    "variant, expected_string",
    [
        (CommonKwargs.IsPipeline, "is_pipeline"),
        (CommonKwargs.ModelType, "model_type"),
        (CommonKwargs.ModelClass, "model_class"),
        (CommonKwargs.ModelArch, "model_arch"),
        (CommonKwargs.PreprocessorName, "preprocessor_name"),
        (CommonKwargs.Preprocessor, "preprocessor"),
        (CommonKwargs.TaskType, "task_type"),
        (CommonKwargs.Model, "model"),
        (CommonKwargs.Undefined, "undefined"),
        (CommonKwargs.Backend, "backend"),
        (CommonKwargs.Pytorch, "pytorch"),
        (CommonKwargs.Tensorflow, "tensorflow"),
        (CommonKwargs.SampleData, "sample_data"),
        (CommonKwargs.Onnx, "onnx"),
        (CommonKwargs.LoadType, "load_type"),
        (CommonKwargs.DataType, "data_type"),
        (CommonKwargs.Tokenizer, "tokenizer"),
        (CommonKwargs.TokenizerName, "tokenizer_name"),
        (CommonKwargs.FeatureExtractor, "feature_extractor"),
        (CommonKwargs.FeatureExtractorName, "feature_extractor_name"),
        (CommonKwargs.Image, "image"),
        (CommonKwargs.Text, "text"),
        (CommonKwargs.VowpalArgs, "arguments"),
        (CommonKwargs.BaseVersion, "0.0.0"),
        (CommonKwargs.SampleDataInterfaceType, "sample_data_interface_type"),
    ],
)
def test_common_kwargs_as_string(variant, expected_string):
    assert variant.as_string() == expected_string


@pytest.mark.parametrize(
    "variant, expected_string",
    [
        (SaveName.Card, "card"),
        (SaveName.Audit, "audit"),
        (SaveName.PipelineCard, "pipelinecard"),
        (SaveName.ModelMetadata, "model-metadata"),
        (SaveName.TrainedModel, "trained-model"),
        (SaveName.Preprocessor, "preprocessor"),
        (SaveName.OnnxModel, "onnx-model"),
        (SaveName.SampleModelData, "sample-model-data"),
        (SaveName.DataProfile, "data-profile"),
        (SaveName.Data, "data"),
        (SaveName.Profile, "profile"),
        (SaveName.Artifacts, "artifacts"),
        (SaveName.QuantizedModel, "quantized-model"),
        (SaveName.Tokenizer, "tokenizer"),
        (SaveName.FeatureExtractor, "feature_extractor"),
        (SaveName.Metadata, "metadata"),
        (SaveName.Graphs, "graphs"),
        (SaveName.OnnxConfig, "onnx-config"),
        (SaveName.Dataset, "dataset"),
        (SaveName.DriftProfile, "drift-profile"),
    ],
)
def test_save_name_as_string(variant, expected_string):
    assert variant.as_string() == expected_string


@pytest.mark.parametrize(
    "variant, expected_string",
    [
        (Suffix.Onnx, ".onnx"),
        (Suffix.Parquet, ".parquet"),
        (Suffix.Zarr, ".zarr"),
        (Suffix.Joblib, ".joblib"),
        (Suffix.Html, ".html"),
        (Suffix.Json, ".json"),
        (Suffix.Ckpt, ".ckpt"),
        (Suffix.Pt, ".pt"),
        (Suffix.Text, ".txt"),
        (Suffix.Catboost, ".cbm"),
        (Suffix.Jsonl, ".jsonl"),
        (Suffix.Empty, ""),
        (Suffix.Dmatrix, ".dmatrix"),
        (Suffix.Model, ".model"),
    ],
)
def test_suffix_as_string(variant, expected_string):
    assert variant.as_string() == expected_string


def test_opsml_config():
    config = OpsmlConfig()
    assert config is not None


def test_version_type_enum():
    assert VersionType.Major == VersionType.Major
    assert VersionType.Minor == VersionType.Minor
    assert VersionType.Patch == VersionType.Patch
    assert VersionType.Pre == VersionType.Pre
    assert VersionType.Build == VersionType.Build
    assert VersionType.PreBuild == VersionType.PreBuild


def test_version_type_from_str():
    assert VersionType("major") == VersionType.Major
    assert VersionType("minor") == VersionType.Minor
    assert VersionType("patch") == VersionType.Patch
    assert VersionType("pre") == VersionType.Pre
    assert VersionType("build") == VersionType.Build
    assert VersionType("pre_build") == VersionType.PreBuild

    with pytest.raises(ValueError):
        VersionType("invalid")


def test_version_type_str():
    assert str(VersionType.Major) == "VersionType.Major"
    assert str(VersionType.Minor) == "VersionType.Minor"
    assert str(VersionType.Patch) == "VersionType.Patch"
    assert str(VersionType.Pre) == "VersionType.Pre"
    assert str(VersionType.Build) == "VersionType.Build"
    assert str(VersionType.PreBuild) == "VersionType.PreBuild"


def test_registry_type_enum():
    assert RegistryType.Data == RegistryType.Data
    assert RegistryType.Model == RegistryType.Model
    assert RegistryType.Project == RegistryType.Project
    assert RegistryType.Audit == RegistryType.Audit
    assert RegistryType.Run == RegistryType.Run
