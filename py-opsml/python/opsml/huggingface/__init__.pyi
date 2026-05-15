from typing import TYPE_CHECKING, Any

from opsml._opsml import HuggingFaceTask, ModelCard, ModelSaveKwargs, TaskType

if TYPE_CHECKING:
    from transformers import PreTrainedModel  # type: ignore[import-not-found]

def log_model(
    model: "PreTrainedModel",
    *,
    name: str,
    space: str | None = None,
    sample_data: Any | None = None,
    tokenizer: Any | None = None,
    feature_extractor: Any | None = None,
    image_processor: Any | None = None,
    hf_task: HuggingFaceTask | None = None,
    task_type: TaskType | None = None,
    drift_profile: Any | None = None,
    save_kwargs: ModelSaveKwargs | None = None,
) -> ModelCard: ...

__all__ = ["log_model"]
