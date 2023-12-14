from opsml.registry.cards.validator import ModelCardValidator
from opsml.model.utils.model_predict_helper import PredictHelper
import pytest
import numpy as np


@pytest.mark.compat
def test_huggingface_model(huggingface_bart):
    model, inputs = huggingface_bart

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "BartModel"
    assert metadata.model_class == "transformers"
    assert metadata.task_type == "unknown"

    predictions = PredictHelper.get_model_prediction(
        model,
        validator.get_sample_data(),
        metadata.sample_data_type,
        metadata.model_class,
        metadata.model_type,
    )

    assert isinstance(predictions, np.ndarray)


@pytest.mark.compat
def test_huggingface_pipeline(huggingface_text_classification_pipeline):
    model, inputs = huggingface_text_classification_pipeline

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "TextClassificationPipeline"
    assert metadata.model_class == "transformers"

    predictions = PredictHelper.get_model_prediction(
        model,
        validator.get_sample_data(),
        metadata.sample_data_type,
        metadata.model_class,
        metadata.model_type,
    )
    assert isinstance(predictions, list)


@pytest.mark.compat
def test_huggingface_subclass(huggingface_subclass):
    model, inputs = huggingface_subclass

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "subclass"
    assert metadata.model_class == "transformers"


@pytest.mark.compat
def test_sklearn_subclass(sklearn_subclass):
    model, inputs = sklearn_subclass

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "subclass"
    assert metadata.model_class == "sklearn_estimator"


@pytest.mark.compat
def test_torch_deeplab(deeplabv3_resnet50):
    model, inputs = deeplabv3_resnet50

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "DeepLabV3"
    assert metadata.model_class == "pytorch"

    predictions = PredictHelper.get_model_prediction(
        model,
        validator.get_sample_data(),
        metadata.sample_data_type,
        metadata.model_class,
        metadata.model_type,
    )

    assert isinstance(predictions, dict)


@pytest.mark.compat
def test_torch_lightning(pytorch_lightning_model):
    trainer, inputs = pytorch_lightning_model

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=trainer,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "SimpleModel"
    assert metadata.model_class == "pytorch_lightning"

    predictions = PredictHelper.get_model_prediction(
        trainer.model,
        validator.get_sample_data(),
        metadata.sample_data_type,
        metadata.model_class,
        metadata.model_type,
    )

    assert isinstance(predictions, np.ndarray)

    with pytest.raises(ValueError) as e:
        validator = ModelCardValidator(
            sample_data=inputs,
            trained_model=trainer.model,
        )
        metadata = validator.get_metadata()

    e.match("Trainer must be passed to ModelCardValidator when using pytorch lightning models")


@pytest.mark.compat
def test_sklearn_pipeline(sklearn_pipeline):
    model, inputs = sklearn_pipeline

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "sklearn_pipeline"
    assert metadata.model_class == "sklearn_estimator"

    predictions = PredictHelper.get_model_prediction(
        model,
        validator.get_sample_data(),
        metadata.sample_data_type,
        metadata.model_class,
        metadata.model_type,
    )
    assert isinstance(predictions, np.ndarray)


@pytest.mark.compat
def test_tensorflow(load_transformer_example):
    model, inputs = load_transformer_example

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "Functional"
    assert metadata.model_class == "keras"

    predictions = PredictHelper.get_model_prediction(
        model,
        validator.get_sample_data(),
        metadata.sample_data_type,
        metadata.model_class,
        metadata.model_type,
    )

    assert isinstance(predictions, np.ndarray)


@pytest.mark.compat
def test_tensorflow_multi_input(load_multi_input_keras_example):
    model, inputs = load_multi_input_keras_example

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "Functional"
    assert metadata.model_class == "keras"

    predictions = PredictHelper.get_model_prediction(
        model,
        validator.get_sample_data(),
        metadata.sample_data_type,
        metadata.model_class,
        metadata.model_type,
    )

    assert isinstance(predictions, list)
