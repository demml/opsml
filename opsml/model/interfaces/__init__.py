from typing import Union

from opsml.model.interfaces.base import (
    ModelInterface,
    SamplePrediction,
    get_model_interface,
)
from opsml.model.interfaces.huggingface import HuggingFaceModel
from opsml.model.interfaces.lgbm import LightGBMModel
from opsml.model.interfaces.pytorch import PyTorchModel
from opsml.model.interfaces.pytorch_lightning import LightningModel
from opsml.model.interfaces.sklearn import SklearnModel
from opsml.model.interfaces.tf import TensorFlowModel
from opsml.model.interfaces.xgb import XGBoostModel
