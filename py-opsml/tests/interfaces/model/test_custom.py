from opsml.model import (
    ModelInterface,
    TaskType,
    ModelInterfaceMetadata,
    ModelInterfaceSaveMetadata,
    ModelSaveKwargs,
    ModelLoadKwargs,
)
from sklearn import linear_model  # type: ignore
from pathlib import Path


class CustomInterface(ModelInterface):
    # must be defined if you want to pass args to ModelInterface
    def __new__(cls, foo=None, **kwargs):
        instance = super(CustomInterface, cls).__new__(cls, **kwargs)
        return instance

    def __init__(self, foo, **kwargs):
        super().__init__()

        self.foo = foo

    def save(
        self,
        path: Path,
        to_onnx: bool = False,
        save_kwargs: ModelSaveKwargs | None = None,
    ) -> ModelInterfaceMetadata:
        model_save_path = Path("model").with_suffix(".joblib")

        # joblib.dump(self.model, path / model_save_path)

        save_metadata = ModelInterfaceSaveMetadata(model_uri=model_save_path)

        return ModelInterfaceMetadata(
            task_type=self.task_type,
            model_type=self.model_type,
            data_type=self.data_type,
            save_metadata=save_metadata,
            extra_metadata={"foo": str(self.foo)},
        )

    def load(
        self,
        path: Path,
        metadata: ModelInterfaceSaveMetadata,
        load_kwargs: ModelLoadKwargs | None = None,
    ) -> None:
        model_path = path / metadata.model_uri

        # self.model = joblib.load(model_path)
        self.model = None


def test_custom_interface(tmp_path: Path, regression_data):
    X, y = regression_data
    reg = linear_model.LinearRegression().fit(X, y)

    kwargs = {"model": reg, "task_type": TaskType.Regression, "sample_data": X}
    interface = CustomInterface(foo=2, **kwargs)

    interface.save(tmp_path, False)
