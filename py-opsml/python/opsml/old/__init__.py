# type: ignore
# pylint: disable=no-name-in-module,import-error
# opsml/__init__.py

from .card import (
    Card,
    CardRegistries,
    CardRegistry,
    DataCard,
    DataCardMetadata,
    ExperimentCard,
    ModelCard,
    ModelCardMetadata,
    PromptCard,
    RegistryType,
    ServiceCard,
)
from .opsml import (  # noqa: F401
    app,
    card,
    cli,
    data,
    evaluate,
    experiment,
    genai,
    get_opsml_version,
    logging,
    mock,
    model,
    scouter,
    types,
)

HuggingFaceOnnxArgs = model.HuggingFaceOnnxArgs
HuggingFaceORTModel = model.HuggingFaceORTModel
HuggingFaceTask = model.HuggingFaceTask
ModelInterfaceSaveMetadata = model.ModelInterfaceSaveMetadata
ModelInterface = model.ModelInterface
TaskType = model.TaskType
SklearnModel = model.SklearnModel
DataProcessor = model.DataProcessor
LightGBMModel = model.LightGBMModel
ModelType = model.ModelType
XGBoostModel = model.XGBoostModel
TorchModel = model.TorchModel
LightningModel = model.LightningModel
HuggingFaceModel = model.HuggingFaceModel
CatBoostModel = model.CatBoostModel
OnnxModel = model.OnnxModel
OnnxSession = model.OnnxSession
TensorFlowModel = model.TensorFlowModel
ModelLoadKwargs = model.ModelLoadKwargs
ModelSaveKwargs = model.ModelSaveKwargs


PandasData = data.PandasData
PolarsData = data.PolarsData
ArrowData = data.ArrowData
NumpyData = data.NumpyData
TorchData = data.TorchData
SqlData = data.SqlData
DataInterface = data.DataInterface
DataSaveKwargs = data.DataSaveKwargs
DataLoadKwargs = data.DataLoadKwargs


start_experiment = experiment.start_experiment
get_experiment_metrics = experiment.get_experiment_metrics
get_experiment_parameters = experiment.get_experiment_parameters

# logging
RustyLogger = logging.RustyLogger
LoggingConfig = logging.LoggingConfig
WriteLevel = logging.WriteLevel
LogLevel = logging.LogLevel


VersionType = types.VersionType

# Potato Head
Prompt = genai.Prompt
Message = genai.Message
ModelSettings = genai.ModelSettings


# CLI
run_opsml_cli = cli.run_opsml_cli

__version__ = get_opsml_version()


__all__ = [
    "CardRegistry",
    "CardRegistries",
    "RegistryType",
    "ModelCard",
    "ModelCardMetadata",
    "HuggingFaceOnnxArgs",
    "HuggingFaceORTModel",
    "HuggingFaceTask",
    "ModelInterfaceSaveMetadata",
    "ModelInterface",
    "TaskType",
    "SklearnModel",
    "DataProcessor",
    "LightGBMModel",
    "ModelType",
    "XGBoostModel",
    "TorchModel",
    "LightningModel",
    "HuggingFaceModel",
    "CatBoostModel",
    "OnnxModel",
    "OnnxSession",
    "TensorFlowModel",
    "ModelLoadKwargs",
    "ModelSaveKwargs",
    "DataCard",
    "DataCardMetadata",
    "PandasData",
    "PolarsData",
    "ArrowData",
    "NumpyData",
    "TorchData",
    "SqlData",
    "DataInterface",
    "DataSaveKwargs",
    "DataLoadKwargs",
    "ExperimentCard",
    "start_experiment",
    "get_experiment_metrics",
    "get_experiment_parameters",
    "RustyLogger",
    "LoggingConfig",
    "WriteLevel",
    "LogLevel",
    "VersionType",
    "PromptCard",
    "Prompt",
    "Message",
    "ModelSettings",
    "ServiceCard",
    "Card",
    "run_opsml_cli",
    "__version__",
]
