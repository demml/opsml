from pathlib import Path

import pytest
from opsml.model import (
    ModelInterface,
    ModelInterfaceMetadata,
    ModelInterfaceSaveMetadata,
    ModelLoadKwargs,
    ModelSaveKwargs,
    TaskType,
)
from sklearn import linear_model  # type: ignore


class CustomInterface(ModelInterface):
    def __init__(self, foo: int, **kwargs):
        super().__init__(**kwargs)
        self.foo = foo

    def save(
        self,
        path: Path,
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
        _model_path = path / metadata.model_uri

        # self.model = joblib.load(model_path)
        self.model = None


def test_custom_interface(tmp_path: Path, regression_data):
    X, y = regression_data
    reg = linear_model.LinearRegression().fit(X, y)

    kwargs = {"model": reg, "task_type": TaskType.Regression, "sample_data": X}
    interface = CustomInterface(foo=2, **kwargs)

    assert interface.foo == 2
    assert interface.task_type == TaskType.Regression
    interface.save(tmp_path)


def test_model_interface_direct_init(regression_data):
    X, y = regression_data
    reg = linear_model.LinearRegression().fit(X, y)

    interface = ModelInterface(
        model=reg,
        sample_data=X,
        task_type=TaskType.Regression,
    )

    assert interface.task_type == TaskType.Regression


def test_model_interface_direct_init_rejects_unknown_kwargs(regression_data):
    X, y = regression_data
    reg = linear_model.LinearRegression().fit(X, y)

    with pytest.raises(RuntimeError, match="Unexpected ModelInterface.__init__.*typo"):
        ModelInterface(
            model=reg,
            sample_data=X,
            task_type=TaskType.Regression,
            typo=True,
        )
