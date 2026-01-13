# mypy: disable-error-code="attr-defined"
# pylint: disable=no-name-in-module
# python/opsml/__init__.py
from . import (
    app,
    card,
    data,
    experiment,
    genai,
    logging,
    mock,
    model,
    scouter,
    types,
)
from ._opsml import (  # top-level modules; # App; # Card; # Data; Experiment; # model
    AppState,
    ArrowData,
    Card,
    CardRegistries,
    CardRegistry,
    CatBoostModel,
    DataCard,
    DataInterface,
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
    SklearnModel,
    SqlData,
    TaskType,
    TensorFlowModel,
    TorchModel,
    XGBoostModel,
    _get_log_level,
    _log_json,
    get_opsml_version,
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
    "evaluate",
    "app",
    "logging",
    "mock",
    "scouter",
    "genai",
    "cli",
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
