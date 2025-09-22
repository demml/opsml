from opsml.model import SklearnModel, ModelSaveKwargs, ModelLoadKwargs
from pathlib import Path


def test_save_model_interface(tmp_path: Path, random_forest_classifier: SklearnModel):
    interface = random_forest_classifier

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(save_path, ModelSaveKwargs(save_onnx=True))
    metadata.save_metadata.save_kwargs is not None
    assert metadata.version != "undefined"

    interface.model = None

    assert interface.model is None
    assert metadata.save_metadata.data_processor_map.get("preprocessor") is not None
    interface.preprocessor = None
    assert interface.preprocessor is None

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.model is not None
    assert interface.preprocessor is not None


def test_save_model_interface_with_args(
    tmp_path: Path, stacking_regressor: SklearnModel
):
    interface = stacking_regressor

    save_path = tmp_path / "test"
    save_path.mkdir()

    args = ModelSaveKwargs(
        onnx={"target_opset": {"ai.onnx.ml": 3, "": 9}}, save_onnx=True
    )
    metadata = interface.save(save_path, args)

    assert metadata.save_metadata.save_kwargs is not None

    interface.model = None
    assert interface.model is None

    # load model
    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.model is not None


def test_save_kwargs_serialization():
    kwargs = ModelSaveKwargs(
        onnx={"target_opset": {"ai.onnx.ml": 3, "": 9}},
        model={"test": 1},
    )

    json_string = kwargs.model_dump_json()

    loaded_kwargs = ModelSaveKwargs.model_validate_json(json_string)

    assert loaded_kwargs.model_dump_json() == json_string
