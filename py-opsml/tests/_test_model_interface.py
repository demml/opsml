from opsml_core import (
    HuggingFaceORTModel,
    TorchOnnxArgs,
    Feature,
    ModelInterfaceArgs,
    SklearnModelInterfaceArgs,
    CatBoostModelInterfaceArgs,
    HuggingFaceModelInterfaceArgs,
    HuggingFaceOnnxSaveArgs,
    LightGBMModelInterfaceArgs,
    LightningInterfaceArgs,
    TorchInterfaceArgs,
    TensorFlowInterfaceArgs,
    VowpalWabbitInterfaceArgs,
    XGBoostModelInterfaceArgs,
    ModelInterfaceArgsEnum,
    CommonKwargs,
    TorchSaveArgs,
)
from typing import Dict, Tuple
from tests.conftest import MockInterface


def test_model_interface_args_creation(
    card_args: Tuple[Dict[str, Feature], Dict[str, str]],
):
    feature_map, metadata = card_args

    args = ModelInterfaceArgs(
        task_type="classification",
        model_type="sklearn",
        data_type="tabular",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="csv",
        metadata=metadata,
    )

    assert args.task_type == "classification"
    assert args.model_type == "sklearn"
    assert args.data_type == "tabular"
    assert args.modelcard_uid == "1234"
    assert args.feature_map == feature_map
    assert args.sample_data_interface_type == "csv"
    assert args.metadata == metadata


def test_sklearn_model_interface_args_creation(
    card_args: Tuple[Dict[str, Feature], Dict[str, str]],
):
    feature_map, metadata = card_args

    args = SklearnModelInterfaceArgs(
        task_type="classification",
        model_type="sklearn",
        data_type="tabular",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="csv",
        preprocessor_name="StandardScaler",
        metadata=metadata,
    )

    assert args.task_type == "classification"
    assert args.model_type == "sklearn"
    assert args.data_type == "tabular"
    assert args.modelcard_uid == "1234"
    assert args.feature_map == feature_map
    assert args.sample_data_interface_type == "csv"
    assert args.preprocessor_name == "StandardScaler"
    assert args.metadata == metadata


def test_model_interface_args_enum_creation(card_args):
    feature_map, metadata = card_args

    onnx_args = HuggingFaceOnnxSaveArgs(
        HuggingFaceORTModel.OrtAudioClassification,
        "provider",
        True,
    )
    backend = CommonKwargs.Pytorch

    args = HuggingFaceModelInterfaceArgs(
        task_type="classification",
        model_type="huggingface",
        data_type="text",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="json",
        preprocessor_name="BertTokenizer",
        is_pipeline=True,
        backend=backend,
        onnx_args=onnx_args,
        tokenizer_name="bert-base-uncased",
        feature_extractor_name="bert-feature-extractor",
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)

    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "HuggingFace"


def test_model_interface_args_enum_lightgbm(card_args):
    feature_map, metadata = card_args

    args = LightGBMModelInterfaceArgs(
        task_type="classification",
        model_type="lightgbm",
        data_type="tabular",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="csv",
        preprocessor_name="StandardScaler",
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "LightGBM"


def test_model_interface_args_enum_lightning(card_args):
    feature_map, metadata = card_args
    onnx_args = TorchOnnxArgs(
        input_names=["input"],
        output_names=["output"],
    )

    args = LightningInterfaceArgs(
        task_type="classification",
        model_type="lightning",
        data_type="tabular",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="csv",
        preprocessor_name="StandardScaler",
        onnx_args=onnx_args,
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "Lightning"


def test_model_interface_args_enum_sklearn(card_args):
    feature_map, metadata = card_args

    args = SklearnModelInterfaceArgs(
        task_type="classification",
        model_type="sklearn",
        data_type="tabular",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="csv",
        preprocessor_name="StandardScaler",
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "Sklearn"


def test_model_interface_args_enum_tensorflow(card_args):
    feature_map, metadata = card_args

    args = TensorFlowInterfaceArgs(
        task_type="classification",
        model_type="tensorflow",
        data_type="image",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="tfrecord",
        preprocessor_name="ImagePreprocessor",
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "TensorFlow"


def test_model_interface_args_enum_torch(card_args):
    feature_map, metadata = card_args
    onnx_args = TorchOnnxArgs(
        input_names=["input"],
        output_names=["output"],
    )
    save_args = TorchSaveArgs()

    args = TorchInterfaceArgs(
        task_type="classification",
        model_type="torch",
        data_type="text",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="json",
        preprocessor_name="TextPreprocessor",
        onnx_args=onnx_args,
        save_args=save_args,
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "Torch"


def test_model_interface_args_enum_vowpal(card_args):
    feature_map, metadata = card_args

    args = VowpalWabbitInterfaceArgs(
        task_type="classification",
        model_type="vowpal",
        data_type="text",
        modelcard_uid="1234",
        feature_map=feature_map,
        arguments="--loss_function logistic",
        sample_data_interface_type="json",
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "VowpalWabbit"


def test_model_interface_args_enum_xgboost(card_args):
    feature_map, metadata = card_args

    args = XGBoostModelInterfaceArgs(
        task_type="classification",
        model_type="xgboost",
        data_type="tabular",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="csv",
        preprocessor_name="StandardScaler",
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "XGBoost"


def test_model_interface_args_enum_catboost(card_args):
    feature_map, metadata = card_args

    args = CatBoostModelInterfaceArgs(
        task_type="classification",
        model_type="catboost",
        data_type="tabular",
        modelcard_uid="1234",
        feature_map=feature_map,
        sample_data_interface_type="csv",
        preprocessor_name="StandardScaler",
        metadata=metadata,
    )

    enum_args = ModelInterfaceArgsEnum(args)
    assert isinstance(enum_args, ModelInterfaceArgsEnum)
    assert enum_args.type_name() == "CatBoost"


def test_opsml_interface_mixin(mock_interface: MockInterface):
    assert mock_interface.is_interface is True
