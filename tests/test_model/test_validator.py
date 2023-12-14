from opsml.registry.cards.validator import ModelCardValidator
import pytest


def _test_huggingface_model(huggingface_bart):
    model, inputs = huggingface_bart

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "BartModel"
    assert metadata.model_class == "transformers"


def _test_huggingface_pipeline(huggingface_text_classification_pipeline):
    model, inputs = huggingface_text_classification_pipeline

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "TextClassificationPipeline"
    assert metadata.model_class == "transformers"


def _test_huggingface_subclass(huggingface_subclass):
    model, inputs = huggingface_subclass

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "subclass"
    assert metadata.model_class == "transformers"


def _test_sklearn_subclass(sklearn_subclass):
    model, inputs = sklearn_subclass

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "subclass"
    assert metadata.model_class == "sklearn_estimator"


def _test_torch_deeplab(deeplabv3_resnet50):
    model, inputs = deeplabv3_resnet50

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=model,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "DeepLabV3"
    assert metadata.model_class == "pytorch"


def _test_torch_lightning(pytorch_lightning_model):
    trainer, inputs = pytorch_lightning_model

    validator = ModelCardValidator(
        sample_data=inputs,
        trained_model=trainer,
    )

    metadata = validator.get_metadata()

    assert metadata.model_type == "SimpleModel"
    assert metadata.model_class == "pytorch_lightning"

    with pytest.raises(ValueError) as e:
        validator = ModelCardValidator(
            sample_data=inputs,
            trained_model=trainer.model,
        )
        metadata = validator.get_metadata()

    e.match("Trainer must be passed to ModelCardValidator when using pytorch lightning models")
