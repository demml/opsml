# pylint: disable=[import-outside-toplevel]
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional, Type, Union, cast

import joblib
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
import zarr

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import all_subclasses
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.model.interfaces import (
    HuggingFaceModel,
    LightningModel,
    PyTorchModel,
    TensorFlowModel,
)
from opsml.registry.storage import client
from opsml.registry.storage.downloader import Downloader
from opsml.registry.types import (
    AllowedDataType,
    ArtifactStorageType,
    CommonKwargs,
    FilePath,
    HuggingFaceOnnxArgs,
    HuggingFaceStorageArtifact,
    OnnxModel,
    SaveName,
    StorageRequest,
    UriNames,
)
from opsml.registry.types.model import ModelProto, TrainedModelType

logger = ArtifactLogger.get_logger()


class ArtifactStorage:
    """Artifact storage base class to inherit from"""

    def __init__(
        self,
        artifact_type: str,
        file_suffix: Optional[str] = None,
    ):
        """Instantiates base ArtifactStorage class

        Args:
            artifact_type: Type of artifact. Examples include pyarrow Table, JSON, Pytorch
            storage_client: Backend storage client to use when saving and loading an artifact
            file_suffix: Optional suffix to use when saving and loading an artifact
        """

        self.file_suffix = file_suffix
        self.artifact_type = artifact_type

    @property
    def storage_filesystem(self) -> Any:
        return client.storage_client.client

    @property
    def storage_client(self) -> client.StorageClientType:
        return client.storage_client

    def _upload_artifact(
        self,
        client_path: Path,
        server_path: Path,
        recursive: bool = False,
        **kwargs: Any,
    ) -> str:
        """Carries out post processing for proxy clients

        Args:
            client_path:
                Path on client to upload
            server_path:
                Path on server to upload to
            recursive:
                Whether to recursively upload all files and folder in a given path
        """

        return self.storage_client.upload(
            local_path=client_path,
            write_path=server_path,
            recursive=recursive,
            **kwargs,
        )

    def _load_artifact(self, file_path: FilePath) -> Any:
        raise NotImplementedError

    def _save_artifact(self, artifact: Any, server_path: Path, client_path: Path) -> str:
        """Saves an artifact"""
        raise NotImplementedError()

    def save_artifact(self, artifact: Any, storage_request: StorageRequest) -> str:
        # set storage path for server
        server_path = storage_request.uri_path

        # create tmp dir for client
        with tempfile.TemporaryDirectory() as client_dir:
            file_name = storage_request.filename or uuid.uuid4().hex
            client_path = Path(client_dir, file_name)
            if self.file_suffix is not None:
                client_path.with_suffix(self.file_suffix)

            # check path in case of uploading previously uploaded
            # Mainly for update_card method
            if bool(self.storage_client.list_files(storage_uri=str(server_path))):
                logger.warning("File already exists at {}. Overwriting", str(server_path))

            # for new items
            else:
                server_path = server_path / file_name
                if self.file_suffix is not None:
                    server_path.with_suffix(self.file_suffix)

            # save artifact
            return self._save_artifact(
                artifact=artifact,
                server_path=server_path,
                client_path=client_path,
            )

    def load_artifact(self, lpath: str, **kwargs: Any) -> Any:
        return self._load_artifact(file_path=lpath, **kwargs)

    def save_artifact(self, artifact: Any, root_uri: str, filename: str) -> str:
        if self.file_suffix is not None:
            filename += f".{self.file_suffix}"
        path = os.path.join(root_uri, filename)

        with FileUtils.create_tmp_path(path) as tmp_uri:
            return self._save_artifact(artifact, storage_uri=path, tmp_uri=tmp_uri)

    def _load_artifact(self, file_path: str) -> Any:
        raise NotImplementedError()

    def load_artifact(self, storage_uri: str, **kwargs: Any) -> Any:
        """Loads a single file artifact.

        Artifacts that represent directories must override load_artifact and
        implement their own loading behavior.
        """

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = os.path.join(tmpdirname, os.path.basename(storage_uri))
            uri = self.storage_client.get(storage_uri, tmppath, recursive=False)
            return self._load_artifact(uri)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        """validate table type"""
        raise NotImplementedError()


class OnnxStorage(ArtifactStorage):
    """Class that saves and onnx model"""

    def __init__(self, artifact_type: str):
        super().__init__(artifact_type=artifact_type, file_suffix=SaveName.ONNX.value)

    def _save_artifact(self, artifact: Any, server_path: Path, client_path: Path) -> str:
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

        _ = client_path.write_bytes(artifact)
        return self._upload_artifact(file_path=client_path, storage_uri=server_path)

    def _load_artifact(self, file_path: FilePath) -> ModelProto:
        from onnx import load

        return cast(ModelProto, load(open(file_path, mode="rb")))

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == SaveName.ONNX


class JoblibStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(self, artifact_type: str):
        super().__init__(artifact_type=artifact_type, file_suffix=SaveName.JOBLIB.value)

    def _save_artifact(self, artifact: Any, server_path: Path, client_path: Path) -> str:
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

        joblib.dump(artifact, str(client_path))
        return self._upload_artifact(client_path, server_path)

    def _load_artifact(self, file_path: str) -> Any:
        return joblib.load(file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == AllowedDataType.JOBLIB


class ImageDataStorage(ArtifactStorage):
    """Class that uploads and downloads image data"""

    def __init__(
        self,
        artifact_type: str,
    ):
        super().__init__(
            artifact_type=artifact_type,
        )

    def _save_artifact(self, artifact: ImageDataset, server_path: Path, client_path: Path) -> str:
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
        storage_path = server_path / artifact.image_dir
        return self.storage_client.upload(
            local_path=artifact.image_dir,
            write_path=str(storage_path),
            is_dir=True,
        )

    def _load_artifact(self, file_path: FilePath) -> None:
        """Not implemented"""

    def load_artifact(self, storage_uri: str, **kwargs: Any) -> None:
        image_dir = kwargs.get("image_dir")
        assert image_dir is not None
        self.storage_client.get(storage_uri, image_dir, True)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.IMAGE


class ParquetStorage(ArtifactStorage):
    """Class that saves and loads a parquet file"""

    def __init__(self, artifact_type: str):
        super().__init__(artifact_type=artifact_type, file_suffix=SaveName.PARQUET.value)

    def _save_artifact(self, artifact: Any, server_path: Path, client_path: Path) -> str:
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
        pq.write_table(table=artifact, where=str(client_path), filesystem=self.storage_filesystem)

        return self.storage_client.upload(
            local_path=str(client_path),
            write_path=str(server_path),
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

        if self.artifact_type == ArtifactStorageType.POLARS:
            return pl.from_arrow(data=pa_table)

        return pa_table

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type in [
            ArtifactStorageType.PYARROW,
            ArtifactStorageType.PANDAS,
            ArtifactStorageType.POLARS,
        ]


class NumpyStorage(ArtifactStorage):
    """Class that saves and loads a numpy ndarray"""

    def __init__(self, artifact_type: str):
        super().__init__(artifact_type=artifact_type)

    def _save_artifact(self, artifact: Any, server_path: Path, client_path: Path) -> str:
        """
            Writes the artifact as a zarr array to the specified storage location

        def _load_artifact(self, file_path: str) -> Any:
            return zarr.load(file_path)

            Returns:
                Storage path
        """

        store = self.storage_client.store(storage_uri=str(client_path))
        zarr.save(store, artifact)

        return self.storage_client.upload(
            local_path=str(client_path),
            write_path=str(server_path),
            **{"is_dir": True},
        )

    def _load_artifact(self, file_path: FilePath) -> NDArray[Any]:
        store = self.storage_client.store(
            storage_uri=str(file_path),
            **{"store_type": "download"},
        )
        return zarr.load(store)  # type: ignore

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.NUMPY


class HTMLStorage(ArtifactStorage):
    """Class that saves and loads an html object"""

    def __init__(
        self,
        artifact_type: str,
    ):
        super().__init__(
            artifact_type=artifact_type,
            file_suffix=SaveName.HTML.value,
        )

    def _save_artifact(self, artifact: Any, server_path: Path, client_path: Path) -> str:
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

        client_path.write_text(artifact, encoding="utf-8")
        return self._upload_artifact(client_path, server_path)

    def _load_artifact(self, file_path: str) -> Any:
        return Path(file_path).read_text(encoding="utf-8")

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == SaveName.HTML


class JSONStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(self, artifact_type: str):
        super().__init__(artifact_type=artifact_type, file_suffix=SaveName.JSON.value)

    def _save_artifact(self, artifact: Any, server_path: Path, client_path: Path) -> str:
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

        client_path.write_text(artifact, encoding="utf-8")
        return self._upload_artifact(client_path, server_path)

    def _load_artifact(self, file_path: str) -> Any:
        with open(file_path, encoding="utf-8") as json_file:
            return json.load(json_file)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == SaveName.JSON


class TensorFlowModelStorage(ArtifactStorage):
    """Class that saves and loads a tensorflow model"""

    def __init__(
        self,
        artifact_type: str,
    ):
        super().__init__(artifact_type=artifact_type)

    def _save_artifact(self, artifact: TensorFlowModel, server_path: Path, client_path: Path) -> str:
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

        artifact.model.save(str(client_path))
        return self._upload_artifact(
            file_path=str(client_path),
            storage_uri=str(server_path),
            recursive=True,
            **{"is_dir": True},
        )

    def _load_artifact(self, file_path: FilePath, **kwargs: Any) -> TensorFlowModel:
        import tensorflow as tf

        tf_model: TensorFlowModel = kwargs[CommonKwargs.MODEL]
        tf_model.model = tf.keras.models.load_model(file_path)
        return tf_model

    def load_artifact(self, storage_uri: str, **kwargs: Any) -> Any:
        with tempfile.TemporaryDirectory() as tmpdirname:
            uri = self.storage_client.get(storage_uri, tmpdirname, recursive=True)
            return self._load_artifact(uri)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == TrainedModelType.TF_KERAS


class PyTorchModelStorage(ArtifactStorage):
    """Class that saves and loads a pytorch model"""

    def __init__(
        self,
        artifact_type: str,
    ):
        super().__init__(artifact_type=artifact_type, file_suffix="pt")

    def _save_artifact(self, artifact: PyTorchModel, server_path: Path, client_path: Path) -> str:
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

        torch.save(artifact.model, client_path)
        return self._upload_artifact(client_path, server_path)

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

    def __init__(self, artifact_type: str):
        super().__init__(artifact_type=artifact_type, file_suffix="ckpt")

    def _save_artifact(self, artifact: LightningModel, server_path: Path, client_path: Path) -> str:
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
        trainer.save_checkpoint(client_path)

        return self._upload_artifact(client_path, server_path)

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

    def __init__(self, artifact_type: str):
        super().__init__(artifact_type=artifact_type)
        self.saved_metadata = {
            CommonKwargs.MODEL.value: False,
            CommonKwargs.PREPROCESSOR.value: False,
            CommonKwargs.ONNX.value: False,
        }

    def _convert_to_onnx(self, artifact: HuggingFaceStorageArtifact, client_path: Path, model_path: Path) -> None:
        # set args
        model_interface: HuggingFaceModel = artifact.model_interface

        logger.info("Converting HuggingFace model to onnx format")
        import onnx
        import optimum.onnxruntime as ort

        # model must be created from directory
        ort_model: ort.ORTModel = getattr(ort, model_interface.onnx_args.ort_type)
        onnx_path = client_path / CommonKwargs.ONNX.value
        onnx_model = ort_model.from_pretrained(
            model_path,
            export=True,
            config=model_interface.onnx_args.config,
            provider=model_interface.onnx_args.provider,
        )
        onnx_model.save_pretrained(onnx_path)
        self.saved_metadata[CommonKwargs.ONNX.value] = True

        # set model_interface
        if model_interface.is_pipeline:
            from transformers import pipeline

            model_interface.onnx_model = OnnxModel(
                onnx_version=onnx.__version__,
                sess=pipeline(
                    model_interface.task_type,
                    model=onnx_model,
                    tokenizer=model_interface.model.tokenizer,
                ),
            )

        else:
            model_interface.onnx_model = onnx_model

    def _save_model(self, artifact: HuggingFaceStorageArtifact, client_path: Path) -> Path:
        """Saves a huggingface model to directory"""

        logger.info("Saving HuggingFace model")
        model_interface: HuggingFaceModel = artifact.model_interface
        model_path = client_path / CommonKwargs.MODEL.value
        model_interface.model.save_pretrained(model_path)
        self.saved_metadata[CommonKwargs.MODEL.value] = True

        # save preprocessor if present
        if model_interface.preprocessor is not None:
            logger.info("Saving HuggingFace preprocessor")
            preprocessor_path = client_path / CommonKwargs.PREPROCESSOR.value
            model_interface.preprocessor.save_pretrained(preprocessor_path)
            self.saved_metadata[CommonKwargs.PREPROCESSOR.value] = True

        return model_path

    def _set_uris(self, artifact: HuggingFaceStorageArtifact, registered_path: str) -> None:
        """Sets metadata uris after uploading to server"""

        artifact.uris[UriNames.TRAINED_MODEL_URI.value] = str(Path(registered_path, CommonKwargs.MODEL.value))

        if self.saved_metadata[CommonKwargs.PREPROCESSOR.value]:
            artifact.uris[UriNames.PREPROCESSOR_URI.value] = str(Path(registered_path, CommonKwargs.PREPROCESSOR.value))

        if self.saved_metadata[CommonKwargs.ONNX.value]:
            artifact.uris[UriNames.ONNX_MODEL_URI.value] = str(Path(registered_path, CommonKwargs.ONNX.value))

    def _set_metadata(self, artifact: HuggingFaceStorageArtifact) -> None:
        from opsml.registry.model.model_converters import _TrainedModelMetadataCreator

        metadata = _TrainedModelMetadataCreator(artifact=artifact.model_interface).get_model_metadata()

        if self.saved_metadata[CommonKwargs.ONNX.value]:
            from opsml.registry.model.model_converters import _ModelConverter

            onnx_input_features, onnx_output_features = _ModelConverter(
                artifact=artifact.model_interface,
            ).create_feature_dict(artifact.model_interface.onnx_model.sess)

            metadata.data_schema.onnx_input_features = onnx_input_features
            metadata.data_schema.onnx_output_features = onnx_output_features
            metadata.data_schema.onnx_data_type = AllowedDataType.NUMPY.value

        artifact.metadata.data_schema = metadata.data_schema

    def _save_artifact(self, artifact: HuggingFaceStorageArtifact, server_path: Path, client_path: Path) -> str:
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

        model_path = self._save_model(artifact, client_path)

        if artifact.to_onnx:
            assert isinstance(
                artifact.model_interface.onnx_args, HuggingFaceOnnxArgs
            ), "onnx_args must be provided when saving a converting a huggingface model"

            self._convert_to_onnx(artifact=artifact, client_path=client_path, model_path=model_path)

        registered_path = self._upload_artifact(
            client_path,
            server_path,
            True,
            **{"is_dir": True},
        )

        self._set_uris(artifact=artifact, registered_path=registered_path)
        self._set_metadata(artifact=artifact)

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

    def _load_artifact(self, file_path: str) -> Any:
        import lightgbm as lgb

        return lgb.Booster(model_file=file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == TrainedModelType.LGBM_BOOSTER


def _storage_for_type(artifact_type: ArtifactStorageType) -> Type[ArtifactStorage]:
    for storage_type in all_subclasses(ArtifactStorage):
        if storage_type.validate(artifact_type):
            return storage_type

    return JoblibStorage


def _get_artifact_storage_type(
    artifact_type: Optional[Union[str, ArtifactStorageType]],
    artifact: Optional[Any],
) -> ArtifactStorageType:
    if isinstance(artifact_type, ArtifactStorageType):
        return artifact_type

    # First, try matching the enum type.
    if isinstance(artifact_type, str):
        artifact_storage = ArtifactStorageType.from_str(artifact_type)
        if artifact_storage is not None:
            return artifact_storage

    # Finally, try matching on the class name
    artifact_storage = ArtifactStorageType.from_str(artifact.__class__.__name__)
    if artifact_storage is not None:
        return artifact_storage

    return ArtifactStorageType.JOBLIB


def save_artifact_to_storage(
    artifact: Any,
    storage_request: StorageRequest,
    artifact_type: str,
) -> str:
    storage_type: ArtifactStorage = next(
        (
            storage_type
            for storage_type in ArtifactStorage.__subclasses__()
            if storage_type.validate(
                artifact_type=artifact_type,
            )
        ),
        JoblibStorage,
    )

    return storage_type(artifact_type=artifact_type).save_artifact(
        artifact=artifact,
        storage_request=storage_request,
    )


def load_artifact_from_storage(
    artifact_type: str,
    storage_request: StorageRequest,
    **kwargs: Any,
) -> Any:
    with tempfile.TemporaryDirectory() as lpath:
        Downloader(storage_request=storage_request).download(lpath)
        storage_type = next(
            (
                storage_type
                for storage_type in all_subclasses(ArtifactStorage)
                if storage_type.validate(
                    artifact_type=artifact_type,
                )
            ),
            JoblibStorage,
        )

        return storage_type(artifact_type=artifact_type).load_artifact(
            storage_request=storage_request,
            **kwargs,
        )
