from opsml.registry.cards import ModelCard
from opsml.registry.cards.card_saver import save_card_artifacts
from opsml.registry.model.interfaces import SklearnModel
from opsml.registry.types import SaveName
from pathlib import Path
from tests.conftest import cleanup


def test_save_modelcard_local_client(random_forest_classifier: SklearnModel):
    model: SklearnModel = random_forest_classifier
    modelcard = ModelCard(
        interface=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
        to_onnx=True,
        version="0.0.1",
    )

    save_card_artifacts(modelcard)
    
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx").exists()
    cleanup()
