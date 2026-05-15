from typing import TYPE_CHECKING, Any

from opsml._opsml import ModelCard, ModelSaveKwargs, TaskType

if TYPE_CHECKING:
    from catboost import CatBoost  # type: ignore[import-not-found]

def log_model(
    model: "CatBoost",
    *,
    name: str,
    space: str | None = None,
    sample_data: Any | None = None,
    preprocessor: Any | None = None,
    task_type: TaskType | None = None,
    drift_profile: Any | None = None,
    save_kwargs: ModelSaveKwargs | None = None,
) -> ModelCard: ...

__all__ = ["log_model"]
