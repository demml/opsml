# rom typing import Union
#
# rom opsml.model.interfaces.base import (
#   ModelInterface,
#   SamplePrediction,
#   get_model_interface,
#
from opsml.helpers.utils import all_subclasses
from opsml.model.interfaces.base import ModelInterface
from opsml.model.interfaces.huggingface import HuggingFaceModel
from opsml.model.interfaces.lgbm import LightGBMModel
from opsml.model.interfaces.pytorch import PyTorchModel
from opsml.model.interfaces.pytorch_lightning import LightningModel
from opsml.model.interfaces.sklearn import SklearnModel
from opsml.model.interfaces.tf import TensorFlowModel
from opsml.model.interfaces.xgb import XGBoostModel


def get_model_interface(interface_type: str) -> ModelInterface:
    """Load model interface from pathlib object

    Args:
        interface_type:
            Name of interface
    """
    return next(
        (cls for cls in all_subclasses(ModelInterface) if cls.name() == interface_type),
        ModelInterface,  # type: ignore[arg-type]
    )
