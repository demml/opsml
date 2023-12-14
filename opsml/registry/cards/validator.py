# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Optional, Union, Tuple

import pandas as pd
import polars as pl
from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.model.utils.types import TrainedModelType, ValidModelInput, HuggingFaceModuleType, ModelType
from opsml.registry.cards.types import DataCardMetadata, ModelCardMetadata
from opsml.registry.data.types import AllowedDataType, ValidData, check_data_type

logger = ArtifactLogger.get_logger()


class CardValidator:
    """Base class for card validators to be used during card instantiation"""

    def get_metadata(self) -> Any:
        raise NotImplementedError


class DataCardValidator(CardValidator):
    def __init__(
        self,
        data: ValidData,
        sql_logic: Dict[str, str],
        metadata: Optional[DataCardMetadata] = None,
    ) -> None:
        """DataCardValidator validator to be used during DataCard instantiation

        Args:
            data:
                Data to be used for DataCard
            sql_logic:
                SQL logic to be used for DataCard
            metadata:
                Metadata to be used for DataCard
        """
        self.data = data
        self.metadata = metadata
        self.sql_logic = sql_logic

    @property
    def has_data_uri(self) -> bool:
        """Checks if data uri is present in metadata"""
        if self.metadata is not None:
            return bool(self.check_metadata())
        return False

    def get_data_type(self) -> str:
        """Get data allowed datatype for DataCard"""
        if self.data is None and bool(self.sql_logic):
            return AllowedDataType.SQL
        return check_data_type(self.data)

    def check_metadata(self) -> Optional[str]:
        """Validates metadata

        Returns:
            Data uri if present
        """

        if isinstance(self.metadata, DataCardMetadata):
            data_uri = self.metadata.uris.data_uri
        else:
            assert isinstance(self.metadata, dict)
            data_uri = self.metadata["uris"].get("data_uri")

        if self.data is None and not bool(self.sql_logic):
            if data_uri is None:
                raise ValueError("Data or sql logic must be supplied when no data_uri is present")
        return data_uri

    def get_metadata(self) -> DataCardMetadata:
        """Get metadata for DataCard

        Returns:
            `DataCardMetadata` with updated data_type
        """
        data_type = self.get_data_type()
        if self.metadata is None:
            self.metadata = DataCardMetadata(data_type=data_type)

        elif isinstance(self.metadata, DataCardMetadata):
            self.metadata.data_type = data_type

        elif isinstance(self.metadata, dict):
            self.metadata["data_type"] = data_type

        return self.metadata


class ModelCardValidator:
    def __init__(
        self,
        sample_data: ValidModelInput,
        trained_model: Any,
        metadata: Optional[ModelCardMetadata] = None,
    ) -> None:
        """ModelCardValidator validator to be used during ModelCard instantiation

        Args:
            sample_data:
                Sample data to be used for ModelCard
            trained_model:
                Trained model to be used for ModelCard
            metadata:
                Metadata to be used for ModelCard
        """
        self.sample_data = sample_data
        self.trained_model = trained_model
        self.metadata = metadata
        self.model_module = trained_model.__module__
        self.model_bases = [str(base) for base in trained_model.__class__.__bases__]
        self.model_name = trained_model.__class__.__name__

    def _get_model_class_name(self) -> Tuple[str, str]:
        """Gets class name from model"""

        # check for huggingface
        class_module = self.check_huggingface_model_name()
        if class_module is not None:
            return class_module

        # check for pytorch lightning
        class_module = self.check_pytorch_lightning_model_name()
        if class_module is not None:
            return class_module

        # check for pytorch
        class_module = self.check_pytorch_model_name()
        if class_module is not None:
            return class_module

        # check for tensorflow
        class_module = self.check_tf_keras_model_name()
        if class_module is not None:
            return class_module

        # check sklearn
        class_module = self.check_sklearn_model_name()
        if class_module is not None:
            return class_module

        # check for lightgbm
        class_module = self.check_lightgbm_model_name()
        if class_module is not None:
            return class_module

        return str(self.model_module), "unknown"  # will default to joblib storage

    def check_pytorch_lightning_model_name(self) -> Optional[Tuple[str, str]]:
        """Checks if model is a pytorch lightning model. Assumes a trainer
        is passed to the ModelCardValidator
        """
        if "lightning.pytorch" in self.model_module:
            if "trainer" not in self.model_module:
                raise ValueError("Trainer must be passed to ModelCardValidator when using pytorch lightning models")
            return TrainedModelType.PYTORCH_LIGHTNING.value, self.trained_model.model.__class__.__name__

        for base in self.model_bases:
            if "lightning.pytorch" in base:
                if "trainer" not in base:
                    raise ValueError("Trainer must be passed to ModelCardValidator when using pytorch lightning models")
                return TrainedModelType.PYTORCH_LIGHTNING.value, "subclass"

        return None

    def check_lightgbm_model_name(self) -> Optional[Tuple[str, str]]:
        """Checks if model is a lightgbm booster"""

        if "lightgbm" in self.model_module:
            return TrainedModelType.LGBM_BOOSTER.value, self.model_name

        return None

    def check_sklearn_model_name(self) -> Optional[Tuple[str, str]]:
        """Checks if model is from sklearn"""

        if "sklearn" in self.model_module:
            return TrainedModelType.SKLEARN_ESTIMATOR.value, self.model_name

        # check for subclassed models
        for base in self.model_bases:
            if "sklearn" in base:
                return TrainedModelType.SKLEARN_ESTIMATOR.value, "subclass"

        return None

    def check_tf_keras_model_name(self) -> Optional[Tuple[str, str]]:
        """Checks if model is from tensorflow"""

        if "keras" in self.model_module:
            return TrainedModelType.TF_KERAS.value, self.model_name

        # check for subclassed models
        for base in self.model_bases:
            if "keras" in base:
                return TrainedModelType.TF_KERAS.value, "subclass"

        return None

    def check_pytorch_model_name(self) -> Optional[Tuple[str, str]]:
        """Checks if model is from pytorch"""
        for base in self.model_bases:
            if "torch" in base:
                return TrainedModelType.PYTORCH.value, self.model_name

    def check_huggingface_model_name(self) -> Optional[Tuple[str, str]]:
        """Checks if model is from huggingface"""

        if any(huggingface_module in self.model_module for huggingface_module in HuggingFaceModuleType):
            return TrainedModelType.TRANSFORMERS.value, self.model_name

        # for subclassed models
        if hasattr(self.trained_model, "mro"):
            # check for mro
            bases = [str(base) for base in self.trained_model.mro()]
            for base in bases:
                if any(huggingface_module in base for huggingface_module in HuggingFaceModuleType):
                    return TrainedModelType.TRANSFORMERS.value, "subclass"
        return None

    def get_sample_data(self) -> Optional[Union[str, pd.DataFrame, NDArray[Any], Dict[str, NDArray[Any]]]]:
        """Check sample data and returns one record to be used
        during ONNX conversion and validation

        Returns:
            Sample data with only one record
        """
        if self.sample_data is None:
            return self.sample_data

        if isinstance(self.sample_data, str):
            return self.sample_data

        if not isinstance(self.sample_data, dict):
            if isinstance(self.sample_data, pl.DataFrame):
                self.sample_data = self.sample_data.to_pandas()

            return self.sample_data[0:1]

        sample_dict = {}
        if isinstance(self.sample_data, dict):
            for key, value in self.sample_data.items():
                if hasattr(value, "shape"):
                    if len(value.shape) > 1:
                        sample_dict[key] = value[0:1]
                else:
                    raise ValueError(
                        """Provided sample data is not a valid type. 
                        Must be a dictionary of numpy, torch, or tensorflow tensors."""
                    )

            return sample_dict

        raise ValueError("Provided sample data is not a valid type")

    def get_model_type(self, model_class_name: str) -> str:
        """Get model type for metadata"""
        model_type = next(
            (
                model_type
                for model_type in ModelType.__subclasses__()
                if model_type.validate(model_class_name=model_class_name)
            ),
            None,
        )

        if model_type is None:
            return model_class_name
        return model_type.get_type()

    def _get_task_type(self, model_type: str) -> str:
        """Get task type for metadata. Primarily used for huggingface pipelines

        Args:
            model_type:
                Model type to be used for task type
        """

        if hasattr(self.trained_model, "task"):
            return self.trained_model.task

        if "regressor" in model_type:
            return "regression"

        if "classifier" in model_type:
            return "classification"

        return "unknown"

    def get_metadata(self) -> ModelCardMetadata:
        """Checks metadata for valid values
        Returns:
            `ModelCardMetadata` with updated sample_data_type
        """
        # get base model class and class name
        model_class, model_name = self._get_model_class_name()

        # clean up class name (mainly for sklearn, lgb, xgb)
        model_type = self.get_model_type(model_class_name=model_name)

        # get task type (important for huggingface pipelines)
        task_type = self._get_task_type(model_type=model_type)

        data_type = check_data_type(self.sample_data)

        if self.metadata is None:
            if data_type in [AllowedDataType.IMAGE]:
                raise ValueError(
                    f"""Invalid model data input type. Accepted types are a pandas dataframe, 
                                 numpy array, dictionary of numpy arrays and string. Received {data_type}""",
                )
            self.metadata = ModelCardMetadata(
                sample_data_type=data_type,
                model_class=model_class,
                model_type=model_type,
                task_type=task_type,
            )

        elif self.metadata is not None:
            self.metadata.sample_data_type = data_type
            self.metadata.model_type = model_type
            self.metadata.model_class = model_class

        return self.metadata
