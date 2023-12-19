# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import tempfile
from pathlib import Path
from typing import Any, Optional, cast

import joblib
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
import zarr
from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import all_subclasses
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.model.supported_models import (
    HuggingFaceModel,
    LightningModel,
    PyTorchModel,
    TensorFlowModel,
)
from opsml.registry.storage.client import (
    ArtifactClass,
    StorageClientType,
    StorageSystem,
)
from opsml.registry.types import (
    AllowedDataType,
    ArtifactStorageSpecs,
    ArtifactStorageType,
    CommonKwargs,
    FilePath,
    HuggingFaceOnnxArgs,
    HuggingFaceStorageArtifact,
    StoragePath,
)
from opsml.registry.types.model import ModelProto, TrainedModelType

logger = ArtifactLogger.get_logger()


class ArtifactStorage:
    """Artifact storage base class to inherit from"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        file_suffix: Optional[str] = None,
        artifact_class: Optional[str] = None,
        extra_path: Optional[str] = None,
    ):
        """Instantiates base ArtifactStorage class

        Args:
            artifact_type (str): Type of artifact. Examples include pyarrow Table, JSON, Pytorch
            artifact_class (str): Class that the artifact belongs to. This is either DATA or OTHER
            storage_client (StorageClientType): Backend storage client to use when saving and loading an artifact
            file_suffix (str): Optional suffix to use when saving and loading an artifact

        """

        self.file_suffix = file_suffix
        self.extra_path = extra_path
        self.artifact_type = artifact_type
        self.storage_client = storage_client
        self.artifact_class = artifact_class

    @property
    def is_data(self) -> bool:
        return self.artifact_class == ArtifactClass.DATA

    @property
    def is_storage_a_proxy(self) -> bool:
        return self.storage_client.backend not in [StorageSystem.GCS, StorageSystem.LOCAL, StorageSystem.S3]

    @property
    def is_storage_local(self) -> bool:
        return StorageSystem(self.storage_client.backend) == StorageSystem.LOCAL

    @property
    def storage_filesystem(self) -> Any:
        return self.storage_client.client

    def _upload_artifact(
        self,
        file_path: str,
        storage_uri: str,
        recursive: bool = False,
        **kwargs: Any,
    ) -> str:
        """Carries out post processing for proxy clients

        Args:
            file_path:
                File path used for writing
            storage_uri:
                Storage Uri. Can be the same as file_path
            recursive:
                Whether to recursively upload all files and folder in a given path
        """

        return self.storage_client.upload(
            local_path=file_path,
            write_path=storage_uri,
            recursive=recursive,
            **kwargs,
        )

    def _load_artifact(self, file_path: FilePath) -> Any:
        raise NotImplementedError

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Saves an artifact"""
        raise NotImplementedError

    def save_artifact(self, artifact: Any, storage_spec: ArtifactStorageSpecs) -> StoragePath:
        with self.storage_client.create_temp_save_path_with_spec(
            self.storage_client.extend_storage_spec(
                storage_spec,
                extra_path=self.extra_path,
                file_suffix=self.file_suffix,
            )
        ) as temp_output:
            storage_uri, tmp_uri = temp_output
            storage_uri = self._save_artifact(
                artifact=artifact,
                storage_uri=storage_uri,
                tmp_uri=tmp_uri,
            )

            return StoragePath(uri=storage_uri)

    def _download_artifacts(
        self,
        files: FilePath,
        file_path: str,
        tmp_path: str,
    ) -> Any:
        if self.is_storage_local:
            return file_path

        loadable_path = self.storage_client.download(
            rpath=file_path,
            lpath=tmp_path,
            recursive=False,
            **{"files": files},
        )

        return loadable_path or tmp_path

    def load_artifact(self, storage_uri: str, **kwargs: Any) -> Any:
        files = self.storage_client.list_files(storage_uri=storage_uri)
        with tempfile.TemporaryDirectory() as tmpdirname:
            loadable_filepath = self._download_artifacts(
                files=files,
                file_path=storage_uri,
                tmp_path=tmpdirname,
            )

            artifact = self._load_artifact(file_path=loadable_filepath, **kwargs)

        return artifact

    @staticmethod
    def validate(artifact_type: str) -> bool:
        """validate table type"""
        raise NotImplementedError


class OnnxStorage(ArtifactStorage):
    """Class that saves and onnx model"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="onnx",
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the onnx artifact to onnx file

        Args:
            artifact:
                Artifact to write to onnx
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage clients.

        Returns:
            Storage path
        """

        _ = Path(str(tmp_uri)).write_bytes(artifact)
        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath) -> ModelProto:
        from onnx import load

        return cast(ModelProto, load(Path(str(file_path)).open(mode="rb")))

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.ONNX


class JoblibStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="joblib",
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the artifact as a joblib file to a storage_uri

        Args:
            artifact:
                Artifact to write to joblib
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage client.

        Returns:
            Storage path
        """

        joblib.dump(artifact, tmp_uri)
        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath) -> Any:
        return joblib.load(file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return False


class ImageDataStorage(ArtifactStorage):
    """Class that uploads and downloads image data"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            artifact_class=ArtifactClass.DATA.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: ImageDataset, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes image directory to storage client location

        Args:
            artifact:
                Artifact to write to joblib
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used

        Returns:
            Storage path
        """
        storage_path = f"{storage_uri}/{artifact.image_dir}"
        return self.storage_client.upload(
            local_path=artifact.image_dir,
            write_path=storage_path,
            is_dir=True,
        )

    def _load_artifact(self, file_path: FilePath) -> None:
        """Not implemented"""

    def load_artifact(self, storage_uri: str, **kwargs: Any) -> None:
        files = self.storage_client.list_files(storage_uri=storage_uri)
        self.storage_client.download(
            rpath=storage_uri,
            lpath=str(kwargs.get("image_dir")),
            recursive=kwargs.get("recursive", False),
            files=files,
        )

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return AllowedDataType.IMAGE in artifact_type


class ParquetStorage(ArtifactStorage):
    """Class that saves and loads a parquet file"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="parquet",
            artifact_class=ArtifactClass.DATA.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the artifact as a parquet table to the specified storage location

        Args:
            artifact:
                Parquet table to write
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage client.

        Returns:
            Storage path
        """
        pq.write_table(table=artifact, where=tmp_uri, filesystem=self.storage_filesystem)

        return self.storage_client.upload(
            local_path=tmp_uri,
            write_path=storage_uri,
            **{"is_dir": False},
        )

    def _load_artifact(self, file_path: FilePath) -> Any:
        """
        Loads pyarrow data to original saved type

        Args:
            file_path:
                List of filenames that make up the parquet dataset

        Returns
            Pandas DataFrame, Polars DataFrame or pyarrow table
        """

        pa_table: pa.Table = pq.ParquetDataset(
            path_or_paths=file_path,
            filesystem=self.storage_filesystem,
        ).read()

        if self.artifact_type == AllowedDataType.PANDAS:
            return pa_table.to_pandas()

        if self.artifact_type == AllowedDataType.POLARS:
            return pl.from_arrow(data=pa_table)

        return pa_table

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type in [
            AllowedDataType.PYARROW,
            AllowedDataType.PANDAS,
            AllowedDataType.POLARS,
        ]


class NumpyStorage(ArtifactStorage):
    """Class that saves and loads a numpy ndarray"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            artifact_class=ArtifactClass.DATA.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the artifact as a zarr array to the specified storage location

        Args:
            artifact:
                Numpy array to write
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage client.

        Returns:
            Storage path
        """

        store = self.storage_client.store(storage_uri=tmp_uri)
        zarr.save(store, artifact)

        return self.storage_client.upload(
            local_path=tmp_uri,
            write_path=storage_uri,
            **{"is_dir": True},
        )

    def _load_artifact(self, file_path: FilePath) -> NDArray[Any]:
        store = self.storage_client.store(
            storage_uri=str(file_path),
            **{"store_type": "download"},
        )
        return zarr.load(store)  # type: ignore

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == AllowedDataType.NUMPY


class HTMLStorage(ArtifactStorage):
    """Class that saves and loads an html object"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="html",
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Writes the artifact as a json file to a storage_uri

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used or some storage client.

        Returns:
            Storage path
        """

        Path(tmp_uri).write_text(artifact, encoding="utf-8")
        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath) -> Any:
        return Path(str(file_path)).read_text(encoding="utf-8")

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.HTML


class JSONStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="json",
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Writes the artifact as a json file to a storage_uri

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used or some storage client.

        Returns:
            Storage path
        """

        Path(tmp_uri).write_text(artifact, encoding="utf-8")
        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath) -> Any:
        with open(str(file_path), encoding="utf-8") as json_file:
            return json.load(json_file)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.JSON


class TensorFlowModelStorage(ArtifactStorage):
    """Class that saves and loads a tensorflow model"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix=None,
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: TensorFlowModel, storage_uri: str, tmp_uri: str) -> str:
        """Saves a tensorflow model

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used for some storage clients.

        Returns:
            Storage path
        """

        artifact.model.save(tmp_uri)
        return self._upload_artifact(
            file_path=tmp_uri,
            storage_uri=storage_uri,
            recursive=True,
            **{"is_dir": True},
        )

    def _load_artifact(self, file_path: FilePath, **kwargs: Any) -> TensorFlowModel:
        import tensorflow as tf

        tf_model: TensorFlowModel = kwargs[CommonKwargs.MODEL]
        tf_model.model = tf.keras.models.load_model(file_path)
        return tf_model

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == TrainedModelType.TF_KERAS


class PyTorchModelStorage(ArtifactStorage):
    """Class that saves and loads a pytorch model"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="pt",
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: PyTorchModel, storage_uri: str, tmp_uri: str) -> str:
        """
        Saves a pytorch model

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used for some storage clients.

        Returns:
            Storage path
        """
        import torch

        torch.save(artifact.model, tmp_uri)
        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath, **kwargs: Any) -> PyTorchModel:
        import torch

        torch_model: PyTorchModel = kwargs[CommonKwargs.MODEL]
        torch_model.model = torch.load(str(file_path))

        return torch_model

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == TrainedModelType.PYTORCH


class PyTorchLightningModelStorage(ArtifactStorage):
    """Class that saves and loads a pytorch model"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="ckpt",
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )

    def _save_artifact(self, artifact: LightningModel, storage_uri: str, tmp_uri: str) -> str:
        """
        Saves a pytorch lightning model

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used for some storage clients.

        Returns:
            Storage path
        """
        from lightning import Trainer

        trainer = cast(Trainer, artifact.model)
        trainer.save_checkpoint(tmp_uri)

        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath, **kwargs: Any) -> LightningModel:
        """Loads a pytorch lightning model. It is expected that a model
        architecture will be passed via kwargs in order to load the model from
        a checkpoint. If an architecture is not passed, an attempt to load via
        pytorch will be made.

        Args:
            file_path:
                File path to checkpoint
        """
        l_model: LightningModel = kwargs[CommonKwargs.MODEL]
        model_arch = kwargs[CommonKwargs.MODEL_ARCH]

        try:
            if model_arch is not None:
                # attempt to load checkpoint into model
                l_model.model = model_arch.load_from_checkpoint(file_path)
                return l_model

            else:
                # load via torch
                import torch

                l_model.model = torch.load(file_path)
                return l_model

        except Exception as e:
            raise ValueError(f"Unable to load pytorch lightning model: {e}")

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == TrainedModelType.PYTORCH_LIGHTNING


class HuggingFaceStorage(ArtifactStorage):
    """Class that saves and loads a huggingface model"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        extra_path: Optional[str] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix=None,
            artifact_class=ArtifactClass.OTHER.value,
            extra_path=extra_path,
        )
        self.saved_metadata = {
            CommonKwargs.MODEL.value: False,
            CommonKwargs.PREPROCESSOR.value: False,
            CommonKwargs.ONNX.value: False,
        }

    def _convert_to_onnx(self, artifact: HuggingFaceStorageArtifact, tmp_uri: str, model_path: str) -> None:
        # set args
        args: HuggingFaceOnnxArgs = artifact.metadata.onnx_args
        model_interface: HuggingFaceModel = artifact.model_interface

        logger.info("Converting HuggingFace model to onnx format")
        import optimum.onnxruntime as ort

        # model must be created from directory
        ort_model: ort.ORTModel = getattr(ort, args.ort_type)
        onnx_path = str(Path(tmp_uri, CommonKwargs.ONNX.value))
        onnx_model = ort_model.from_pretrained(model_path, export=True, config=args.config, provider=args.provider)
        onnx_model.save_pretrained(onnx_path)
        self.saved_metadata[CommonKwargs.ONNX.value] = True

        # set model_interface
        if model_interface.is_pipeline:
            from transformers import pipeline

            model_interface.onnx_model = pipeline(
                model_interface.task_type,
                model=onnx_model,
                tokenizer=model_interface.model.tokenizer,
            )

        else:
            model_interface.onnx_model = onnx_model

        # set onnx path
        artifact.metadata.uris.onnx_model_uri = onnx_path

    def _save_model(self, artifact: HuggingFaceStorageArtifact, tmp_uri: str) -> str:
        """Saves a huggingface model to directory"""

        logger.info("Saving HuggingFace model")
        model_interface: HuggingFaceModel = artifact.model_interface
        model_path = str(Path(tmp_uri, CommonKwargs.MODEL.value))
        model_interface.model.save_pretrained(model_path)
        self.saved_metadata[CommonKwargs.MODEL.value] = True

        # save preprocessor if present
        if model_interface.preprocessor is not None:
            logger.info("Saving HuggingFace preprocessor")
            preprocessor_path = str(Path(tmp_uri, CommonKwargs.PREPROCESSOR.value))
            model_interface.preprocessor.save_pretrained(preprocessor_path)
            self.saved_metadata[CommonKwargs.PREPROCESSOR.value] = True

        return model_path

    def _set_uris(self, artifact: HuggingFaceStorageArtifact, registered_path: str) -> None:
        """Sets metadata uris after uploading to server"""

        artifact.metadata.uris.trained_model_uri = str(Path(registered_path, CommonKwargs.MODEL.value))

        if self.saved_metadata[CommonKwargs.PREPROCESSOR.value]:
            artifact.metadata.uris.preprocessor_uri = str(Path(registered_path, CommonKwargs.PREPROCESSOR.value))

        if self.saved_metadata[CommonKwargs.ONNX.value]:
            artifact.metadata.uris.onnx_model_uri = str(Path(registered_path, CommonKwargs.ONNX.value))

    def _save_artifact(self, artifact: HuggingFaceStorageArtifact, storage_uri: str, tmp_uri: str) -> str:
        """
        Saves a huggingface model

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used for some storage clients.

        Returns:
            Storage path
        """

        model_path = self._save_model(artifact, tmp_uri)

        if artifact.to_onnx:
            assert isinstance(
                artifact.model_interface.onnx_args, HuggingFaceOnnxArgs
            ), "onnx_args must be provided when saving a converting a huggingface model"

            self._convert_to_onnx(artifact=artifact, tmp_uri=tmp_uri, model_path=model_path)

        registered_path = self._upload_artifact(
            file_path=tmp_uri,
            storage_uri=storage_uri,
            recursive=True,
            **{"is_dir": True},
        )

        artifact.metadata.uris.trained_model_uri = str(Path(registered_path, CommonKwargs.MODEL.value))

        if self.saved_metadata[CommonKwargs.PREPROCESSOR.value]:
            artifact.metadata.uris.preprocessor_uri = str(Path(registered_path, CommonKwargs.PREPROCESSOR.value))

        if self.saved_metadata[CommonKwargs.ONNX.value]:
            artifact.metadata.uris.onnx_model_uri = str(Path(registered_path, CommonKwargs.ONNX.value))

        return registered_path

    def _load_artifact(self, file_path: FilePath, **kwargs: Any) -> HuggingFaceModel:
        """Loads a huggingface object (model or pipeline)

        Objects are loaded based on kwargs because we don't want to download a specific
        object unless necessary (important for large models)

        Args:
            kwargs:
                Dictionary of arguments to pass to pass for model loading

                model:
                    Load HuggingFaceModel class

        """
        import transformers

        load_type = kwargs[CommonKwargs.LOAD_TYPE]

        if load_type == CommonKwargs.MODEL:
            hf_model: HuggingFaceModel = kwargs[CommonKwargs.MODEL]

            # only way to tell if model was a pipeline is from model class type
            if hf_model.is_pipeline:
                hf_model.model = transformers.pipeline(hf_model.task_type, file_path)
                return hf_model

            else:
                # load model from pretrained
                hf_model.model = getattr(transformers, hf_model.model_type).from_pretrained(file_path)
                return hf_model

        elif load_type == CommonKwargs.PREPROCESSOR:
            hf_model.preprocessor = getattr(transformers, hf_model.preprocessor_name).from_pretrained(file_path)
            return hf_model

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == TrainedModelType.TRANSFORMERS


class LightGBMBoosterStorage(JoblibStorage):
    """Saves a LGBM booster model"""

    def _load_artifact(self, file_path: FilePath) -> Any:
        import lightgbm as lgb

        return lgb.Booster(model_file=file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == TrainedModelType.LGBM_BOOSTER


def save_artifact_to_storage(
    artifact: Any,
    storage_client: StorageClientType,
    storage_spec: ArtifactStorageSpecs,
    artifact_type: Optional[str] = None,
    extra_path: Optional[str] = None,
) -> StoragePath:
    _artifact_type: str = artifact_type or artifact.__class__.__name__

    storage_type = next(
        (
            storage_type
            for storage_type in ArtifactStorage.__subclasses__()
            if storage_type.validate(
                artifact_type=_artifact_type,
            )
        ),
        JoblibStorage,
    )

    return storage_type(
        storage_client=storage_client,
        artifact_type=_artifact_type,
        extra_path=extra_path,
    ).save_artifact(artifact=artifact, storage_spec=storage_spec)


def load_artifact_from_storage(
    artifact_type: str,
    storage_client: StorageClientType,
    storage_spec: ArtifactStorageSpecs,
    **kwargs: Any,
) -> Optional[Any]:
    if not bool(storage_spec.save_path):
        return None

    storage_type = next(
        storage_type
        for storage_type in all_subclasses(ArtifactStorage)
        if storage_type.validate(
            artifact_type=artifact_type,
        )
    )
    return storage_type(
        artifact_type=artifact_type,
        storage_client=storage_client,
    ).load_artifact(storage_uri=storage_spec.save_path, **kwargs)
