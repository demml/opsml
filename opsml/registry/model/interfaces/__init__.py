from typing import Union

from opsml.registry.model.interfaces.base import ModelInterface, SamplePrediction
from opsml.registry.model.interfaces.huggingface import HuggingFaceModel
from opsml.registry.model.interfaces.lgbm import LightGBMBoosterModel
from opsml.registry.model.interfaces.pytorch import PyTorchModel
from opsml.registry.model.interfaces.pytorch_lightning import LightningModel
from opsml.registry.model.interfaces.sklearn import SklearnModel
from opsml.registry.model.interfaces.tf import TensorFlowModel
from opsml.registry.model.interfaces.xgb import XGBoostModel

SUPPORTED_MODELS = Union[
    SklearnModel,
    TensorFlowModel,
    PyTorchModel,
    LightningModel,
    XGBoostModel,
    LightGBMBoosterModel,
    HuggingFaceModel,
]
