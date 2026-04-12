# mypy: disable-error-code="attr-defined"
# pylint: disable=no-name-in-module
# python/opsml/__init__.py
from . import agent, app, card, data, experiment, logging, mock, model, scouter, types
from ._opsml import _get_log_level  # type: ignore
from ._opsml import _log_json  # type: ignore
from ._opsml import get_opsml_version  # type: ignore
from ._opsml import (  # top-level modules; # App; # Card; # Data; Experiment; # model
    AgentSkillStandard,
    AppState,
    ArrowData,
    Card,
    CardRegistries,
    CardRegistry,
    CatBoostModel,
    DataCard,
    DataInterface,
    DependencyKind,
    Experiment,
    ExperimentCard,
    HuggingFaceModel,
    HuggingFaceOnnxArgs,
    HuggingFaceORTModel,
    HuggingFaceTask,
    LightGBMModel,
    LightningModel,
    LoggingConfig,
    ModelCard,
    ModelInterface,
    ModelLoadKwargs,
    ModelSaveKwargs,
    NumpyData,
    OnnxModel,
    PandasData,
    PolarsData,
    Prompt,
    PromptCard,
    RegistryType,
    ReloadConfig,
    RustyLogger,
    ServiceCard,
    SkillCard,
    SkillDependency,
    SklearnModel,
    SqlData,
    TaskType,
    TensorFlowModel,
    TorchModel,
    XGBoostModel,
    start_experiment,
)

__version__: str = get_opsml_version()

# We need to turn on rust logging early if LOG_LEVEL is set
_log_level = _get_log_level()
if _log_level:
    RustyLogger.setup_logging(
        LoggingConfig(
            log_level=_log_level,
            use_json=_log_json(),  # check if LOG_JSON is set to "1" or "true"
        ),
    )

__all__ = [
    "types",
    "card",
    "data",
    "model",
    "experiment",
    "app",
    "logging",
    "mock",
    "scouter",
    "agent",
    ## App
    "AppState",
    "ReloadConfig",
    ## Card
    "Card",
    "CardRegistries",
    "CardRegistry",
    "DataCard",
    "ModelCard",
    "PromptCard",
    "ServiceCard",
    "SkillCard",
    "AgentSkillStandard",
    "SkillDependency",
    "DependencyKind",
    "RegistryType",
    "ExperimentCard",
    ## Data
    "DataInterface",
    "NumpyData",
    "PandasData",
    "PolarsData",
    "SqlData",
    "ArrowData",
    # Experiment
    "start_experiment",
    "Experiment",
    ## model
    "ModelInterface",
    "ModelLoadKwargs",
    "ModelSaveKwargs",
    "SklearnModel",
    "TaskType",
    "TensorFlowModel",
    "TorchModel",
    "XGBoostModel",
    "HuggingFaceModel",
    "HuggingFaceOnnxArgs",
    "HuggingFaceORTModel",
    "HuggingFaceTask",
    "LightGBMModel",
    "LightningModel",
    "CatBoostModel",
    "Prompt",
    "__version__",
    "OnnxModel",
]
