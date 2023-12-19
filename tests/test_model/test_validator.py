from faulthandler import unregister
from typing import Any

import numpy as np
import pytest
from torch import Tensor

from opsml.registry.cards.validator import ModelCardValidator
from opsml.registry.model.supported_models import (
    SUPPORTED_MODELS,
    HuggingFaceModel,
    LightningModel,
    PyTorchModel,
    TensorFlowModel,
)
from opsml.registry.model.utils.model_predict_helper import PredictHelper
from opsml.registry.storage.artifact import (
    load_artifact_from_storage,
    save_artifact_to_storage,
)
from opsml.registry.types import (
    ArtifactStorageSpecs,
    HuggingFaceStorageArtifact,
    ModelCardMetadata,
    HuggingFaceOnnxArgs
)

TRAINED_MODEL = "trained-model"


def simulate_save_load(
    model: SUPPORTED_MODELS,
    api_storage_client: Any,
    metadata: ModelCardMetadata,
    load_model: SUPPORTED_MODELS,
    **kwargs,
) -> SUPPORTED_MODELS:

    if isinstance(model, HuggingFaceModel):
        artifact = HuggingFaceStorageArtifact(
            model_interface=model,
            metadata=metadata,
            to_onnx=True,
        )
    else:
        artifact = model

    storage_path = save_artifact_to_storage(
        artifact=artifact,
        artifact_type=metadata.model_class,
        storage_client=api_storage_client,
        storage_spec=ArtifactStorageSpecs(
            filename=TRAINED_MODEL,
            save_path="OPSML_MODEL_REGISTRY",
        ),
        extra_path="model",
    )

    # simulate dumping and loading prior to loading model
    serialized = model.model_dump(exclude={"model", "preprocessor", "sample_data"})
    serialized["model_uri"] = storage_path.uri
    loaded_model = load_model.model_validate(serialized)

    if isinstance(model, HuggingFaceModel):
        
        loaded_model = load_artifact_from_storage(
            artifact_type=metadata.model_class,
            storage_client=api_storage_client,
            storage_spec=ArtifactStorageSpecs(save_path=metadata.uris.trained_model_uri),
            **{**{"model": loaded_model, "load_type":"model"}, **kwargs},
        )
        
        if metadata.uris.preprocessor_uri is not None:
            loaded_model = load_artifact_from_storage(
                artifact_type=metadata.model_class,
                storage_client=api_storage_client,
                storage_spec=ArtifactStorageSpecs(save_path=metadata.uris.preprocessor_uri),
                **{**{"model": loaded_model, "load_type":"preprocessor"}, **kwargs},
            )

    else:
        loaded_model = load_artifact_from_storage(
            artifact_type=metadata.model_class,
            storage_client=api_storage_client,
            storage_spec=ArtifactStorageSpecs(save_path=storage_path.uri),
            **{**{"model": loaded_model}, **kwargs},
        )

    loaded_model.sample_data = model.sample_data

    return loaded_model


@pytest.mark.compat
def _test_huggingface_model(huggingface_bart, api_storage_client):
    model: HuggingFaceModel = huggingface_bart

    validator = ModelCardValidator(model=model)

    metadata = validator.get_metadata()

    assert metadata.model_type == "BartModel"
    assert metadata.model_class == "transformers"
    assert metadata.task_type == "text-classification"
    assert model.backend == "pytorch"

    predictions = PredictHelper.process_model_prediction(model)

    assert isinstance(predictions, dict)

    loaded_model = simulate_save_load(model, api_storage_client, metadata, HuggingFaceModel)

    assert type(loaded_model.model) == type(model.model)
    assert type(loaded_model.preprocessor) == type(model.preprocessor)


@pytest.mark.compat
def test_huggingface_pipeline(huggingface_text_classification_pipeline, api_storage_client):
    model: HuggingFaceModel = huggingface_text_classification_pipeline

    validator = ModelCardValidator(model=model)

    metadata = validator.get_metadata()

    assert metadata.model_type == "TextClassificationPipeline"
    assert metadata.model_class == "transformers"
    assert metadata.task_type == "text-classification"
    assert model.backend == "pytorch"

    metadata.onnx_args = HuggingFaceOnnxArgs(ort_type="ORTModelForSequenceClassification")
    predictions = PredictHelper.process_model_prediction(model)

    assert isinstance(predictions, dict)
    loaded_model = simulate_save_load(model, api_storage_client, metadata, HuggingFaceModel)
    assert type(loaded_model.model) == type(model.model)


@pytest.mark.compat
def _test_huggingface_tensorflow(huggingface_tf_distilbert, api_storage_client):
    model = huggingface_tf_distilbert

    validator = ModelCardValidator(model=model)
    metadata = validator.get_metadata()

    assert metadata.model_type == "TFDistilBertForSequenceClassification"
    assert metadata.model_class == "transformers"
    assert metadata.task_type == "text-classification"
    assert model.backend == "tensorflow"

    predictions = PredictHelper.process_model_prediction(model)

    assert isinstance(predictions, dict)

    loaded_model = simulate_save_load(model, api_storage_client, metadata, HuggingFaceModel)

    assert type(loaded_model.model) == type(model.model)
    assert type(loaded_model.preprocessor) == type(model.preprocessor)


@pytest.mark.compat
def _test_torch_deeplab(deeplabv3_resnet50, api_storage_client):
    model: PyTorchModel = deeplabv3_resnet50

    validator = ModelCardValidator(model=model)

    metadata = validator.get_metadata()

    assert metadata.model_type == "DeepLabV3"
    assert metadata.model_class == "pytorch"

    predictions = PredictHelper.process_model_prediction(model)
    assert isinstance(predictions, dict)

    loaded_model = simulate_save_load(model, api_storage_client, metadata, PyTorchModel)

    assert type(loaded_model.model) == type(model.model)


@pytest.mark.compat
def _test_torch_lightning(pytorch_lightning_model):
    model: LightningModel = pytorch_lightning_model

    validator = ModelCardValidator(model=model)
    metadata = validator.get_metadata()

    assert metadata.model_type == "SimpleModel"
    assert metadata.model_class == "pytorch_lightning"

    predictions = PredictHelper.process_model_prediction(model)

    assert isinstance(predictions, Tensor)


@pytest.mark.compat
def _test_lightning_regression(lightning_regression, api_storage_client):
    model, arch = lightning_regression

    validator = ModelCardValidator(model)

    metadata = validator.get_metadata()

    assert metadata.model_type == "MyModel"
    assert metadata.model_class == "pytorch_lightning"

    predictions = PredictHelper.process_model_prediction(model)
    assert isinstance(predictions, tuple)

    loaded_model = simulate_save_load(
        model,
        api_storage_client,
        metadata,
        LightningModel,
        **{
            "model_arch": arch,
        },
    )

    assert type(loaded_model.model) == type(model.model.model)


@pytest.mark.compat
def _test_sklearn_pipeline(sklearn_pipeline):
    model = sklearn_pipeline

    validator = ModelCardValidator(model=model)

    metadata = validator.get_metadata()

    assert metadata.model_type == "Pipeline"
    assert metadata.model_class == "sklearn_estimator"

    predictions = PredictHelper.process_model_prediction(model)
    assert isinstance(predictions, np.ndarray)


@pytest.mark.compat
def _test_tensorflow(load_transformer_example, api_storage_client):
    model = load_transformer_example

    validator = ModelCardValidator(model=model)
    metadata = validator.get_metadata()

    assert metadata.model_type == "Functional"
    assert metadata.model_class == "keras"

    predictions = PredictHelper.process_model_prediction(model)
    assert isinstance(predictions, np.ndarray)

    loaded_model = simulate_save_load(model, api_storage_client, metadata, TensorFlowModel)
    assert type(loaded_model.model) == type(model.model)


@pytest.mark.compat
def _test_tensorflow_multi_input(load_multi_input_keras_example, api_storage_client):
    model = load_multi_input_keras_example

    validator = ModelCardValidator(model=model)
    metadata = validator.get_metadata()

    assert metadata.model_type == "Functional"
    assert metadata.model_class == "keras"

    predictions = PredictHelper.process_model_prediction(model)

    assert isinstance(predictions, list)

    loaded_model = simulate_save_load(model, api_storage_client, metadata, TensorFlowModel)
    assert type(loaded_model.model) == type(model.model)
