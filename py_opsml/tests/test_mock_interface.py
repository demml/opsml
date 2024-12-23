from tests.mocks.card import ModelInterface, ModelInterfaceMetadata
from pathlib import Path


def test_model_interface():
    interface = ModelInterface(model={}, sample_data={})

    temp_path = Path("temp")

    metadata = interface.save_interface_artifacts(
        path=temp_path,
        to_onnx=True,
    )

    assert isinstance(metadata, ModelInterfaceMetadata)
