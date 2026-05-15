from typing import TYPE_CHECKING, Any

from opsml._opsml import ModelCard, ModelSaveKwargs, TaskType

if TYPE_CHECKING:
    import onnx  # type: ignore[import-not-found]

def log_model(
    model: "onnx.ModelProto",
    *,
    name: str,
    space: str | None = None,
    sample_data: Any | None = None,
    task_type: TaskType | None = None,
    drift_profile: Any | None = None,
    save_kwargs: ModelSaveKwargs | None = None,
) -> ModelCard: ...

__all__ = ["log_model"]
