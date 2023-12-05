# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Optional, Union

import pandas as pd
import polars as pl
from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.model.model_types import ModelType
from opsml.model.types import TrainedModelType, ValidModelInput
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
        """Get data allowedatatype for DataCard"""
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
        self.model_class = self._get_model_class_name()

    def _get_model_class_name(self) -> str:
        """Gets class name from model"""

        if "keras.engine" in str(self.trained_model):
            return TrainedModelType.TF_KERAS.value

        if "torch" in str(self.trained_model.__class__.__bases__):
            return TrainedModelType.PYTORCH.value

        # for transformer models from huggingface
        if "transformers.models" in str(self.trained_model.__class__.__bases__):
            return TrainedModelType.TRANSFORMER.value

        return str(self.trained_model.__class__.__name__)

    def get_sample(self) -> Optional[Union[pd.DataFrame, NDArray[Any], Dict[str, NDArray[Any]]]]:
        """Check sample data and returns one record to be used
        during ONNX conversion and validation

        Returns:
            Sample data with only one record
        """
        if self.sample_data is None:
            return self.sample_data

        if not isinstance(self.sample_data, dict):
            if isinstance(self.sample_data, pl.DataFrame):
                self.sample_data = self.sample_data.to_pandas()

            return self.sample_data[0:1]

        sample_dict = {}
        if isinstance(self.sample_data, dict):
            for key in self.sample_data.keys():
                sample_dict[key] = self.sample_data[key][0:1]

            return sample_dict

        raise ValueError("Provided sample data is not a valid type")

    def get_model_type(self, model_class: str) -> str:
        """Get model type for ModelCard"""
        model_type = next(
            (
                model_type
                for model_type in ModelType.__subclasses__()
                if model_type.validate(model_class_name=model_class)
            )
        )
        return model_type.get_type()

    def get_metadata(self) -> ModelCardMetadata:
        """Checks metadata for valid values
        Returns:
            `ModelCardMetadata` with updated sample_data_type
        """

        model_class = self._get_model_class_name()
        model_type = self.get_model_type(model_class)
        data_type = check_data_type(self.sample_data)

        if self.metadata is None:
            if data_type in [AllowedDataType.IMAGE]:
                raise ValueError(
                    f"""Invalid model data input type. Accepted types are a pandas dataframe, 
                                 numpy array and dictionary of numpy arrays. Received {data_type}""",
                )
            self.metadata = ModelCardMetadata(
                sample_data_type=data_type,
                model_class=model_class,
                model_type=model_type,
            )

        elif self.metadata is not None:
            self.metadata.sample_data_type = data_type
            self.metadata.model_type = model_type
            self.metadata.model_class = model_class

        return self.metadata
