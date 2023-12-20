# pylint: disable=[import-outside-toplevel]
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import tempfile
from pathlib import Path
from typing import Any, List, Optional, Type, Union, cast

import joblib
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
import zarr
from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import FileUtils, all_subclasses
from opsml.model.types import ModelProto
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.storage.client import StorageClientType
from opsml.registry.storage.types import ArtifactStorageType

logger = ArtifactLogger.get_logger()


class ArtifactStorage:
    """Artifact storage base class to inherit from"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
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
        self.storage_client = storage_client

    @property
    def _storage_filesystem(self) -> Any:
        return self.storage_client.client

    def _upload_artifact(
        self,
        file_path: str,
        storage_uri: str,
        recursive: bool = False,
        **kwargs: Any,
    ) -> str:
        """Uploads an artifact.

        Args:
            file_path (str): File path used for writing
            storage_uri(str): Storage Uri. Can be the same as file_path
            recursive (bool): Whether to recursively upload all files and folder in a given path

        Returns:
            URI of the uploaded artifact

        """

        return self.storage_client.upload(
            local_path=file_path,
            write_path=storage_uri,
            recursive=recursive,
            **kwargs,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Saves an artifact"""
        raise NotImplementedError()

    def save_artifact(self, artifact: Any, root_uri: str, filename: str) -> str:
        path = FileUtils.create_path(
            root_path=root_uri,
            filename=filename,
            suffix=self.file_suffix,
        )
        with self.storage_client.create_tmp_path(path) as tmp_uri:
            return self._save_artifact(artifact, storage_uri=path, tmp_uri=tmp_uri)

    def _download_artifacts(
        self,
        files: List[str],
        file_path: str,
        tmp_path: str,
    ) -> str:
        if self.storage_client.is_local:
            return file_path

        loadable_path = self.storage_client.download(
            rpath=file_path,
            lpath=tmp_path,
            recursive=False,
            **{"files": files},
        )

        return loadable_path or tmp_path

    def _load_artifact(self, file_path: str) -> Any:
        raise NotImplementedError()

    def load_artifact(self, storage_uri: str, **kwargs: Any) -> Any:
        files = self.storage_client.list_files(storage_uri=storage_uri)
        with tempfile.TemporaryDirectory() as tmpdirname:
            loadable_filepath = self._download_artifacts(
                files=files,
                file_path=storage_uri,
                tmp_path=tmpdirname,
            )

            return self._load_artifact(file_path=loadable_filepath, **kwargs)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        """validate table type"""
        raise NotImplementedError()


class OnnxStorage(ArtifactStorage):
    """Class that saves and onnx model"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="onnx",
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

        _ = Path(tmp_uri).write_bytes(artifact)
        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: str) -> Any:
        from onnx import load

        return cast(ModelProto, load(open(file_path, mode="rb")))

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.ONNX


class JoblibStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="joblib",
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

    def _load_artifact(self, file_path: str) -> Any:
        return joblib.load(file_path)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        """JoblibStorage is the default and will be manually set if no other clases match"""
        return False


class ImageDataStorage(ArtifactStorage):
    """Class that uploads and downloads image data"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
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
        storage_path = os.path.join(storage_uri, artifact.image_dir)
        return self.storage_client.upload(
            local_path=artifact.image_dir,
            write_path=storage_path,
            is_dir=True,
        )

    def _load_artifact(self, file_path: str) -> Any:
        raise NotImplementedError()

    def load_artifact(self, storage_uri: str, **kwargs: Any) -> None:
        assert kwargs.get("image_dir") is not None
        files = self.storage_client.list_files(storage_uri=storage_uri)
        self.storage_client.download(
            rpath=storage_uri,
            lpath=str(kwargs.get("image_dir")),
            recursive=kwargs.get("recursive", False),
            files=files,
        )

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.IMAGE


class ParquetStorage(ArtifactStorage):
    """Class that saves and loads a parquet file"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="parquet",
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the artifact as a parquet table to the specified storage location

        Args:
            artifact:
                Parquet gctable to write
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage client.

        Returns:
            Storage path
        """
        pq.write_table(table=artifact, where=tmp_uri, filesystem=self._storage_filesystem)

        return self.storage_client.upload(
            local_path=tmp_uri,
            write_path=storage_uri,
            **{"is_dir": False},
        )

    def _load_artifact(self, file_path: str) -> Any:
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
            filesystem=self._storage_filesystem,
        ).read()

        if self.artifact_type == ArtifactStorageType.PANDAS:
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

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
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

        # TODO(@damon): Make is_dir an upload parameter on storage_client
        return self.storage_client.upload(
            local_path=tmp_uri,
            write_path=storage_uri,
            **{"is_dir": True},
        )

    def _load_artifact(self, file_path: str) -> NDArray[Any]:
        # TODO(@damon): Make store_type a parameter on store
        store = self.storage_client.store(
            storage_uri=file_path,
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
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="html",
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

    def _load_artifact(self, file_path: str) -> Any:
        return Path(file_path).read_text(encoding="utf-8")

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.HTML


class JSONStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="json",
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

    def _load_artifact(self, file_path: str) -> Any:
        with open(file_path, encoding="utf-8") as json_file:
            return json.load(json_file)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.JSON


class TensorflowModelStorage(ArtifactStorage):
    """Class that saves and loads a tensorflow model"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix=None,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
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

        artifact.save(tmp_uri)
        return self._upload_artifact(
            file_path=tmp_uri,
            storage_uri=storage_uri,
            recursive=True,
            **{"is_dir": True},
        )

    def _load_artifact(self, file_path: str) -> Any:
        import tensorflow as tf

        return tf.keras.models.load_model(file_path)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.TF_MODEL


class PyTorchModelStorage(ArtifactStorage):
    """Class that saves and loads a pytorch model"""

    def __init__(
        self,
        artifact_type: ArtifactStorageType,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="pt",
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
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

        torch.save(artifact, tmp_uri)
        return self._upload_artifact(file_path=tmp_uri, storage_uri=storage_uri)

    def _load_artifact(self, file_path: str) -> Any:
        import torch

        return torch.load(file_path)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type in [
            ArtifactStorageType.PYTORCH,
            ArtifactStorageType.TRANSFORMER,
        ]


class LightGBMBoosterStorage(JoblibStorage):
    """Saves a LGBM booster model"""

    def _load_artifact(self, file_path: str) -> Any:
        import lightgbm as lgb

        return lgb.Booster(model_file=file_path)

    @staticmethod
    def validate(artifact_type: ArtifactStorageType) -> bool:
        return artifact_type == ArtifactStorageType.BOOSTER


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

    return ArtifactStorageType.UNKNOWN


def save_artifact_to_storage(
    artifact: Any,
    storage_client: StorageClientType,
    root_uri: str,
    filename: str,
    artifact_type: Optional[Union[str, ArtifactStorageType]] = None,
) -> str:
    _artifact_type = _get_artifact_storage_type(artifact_type, artifact)
    storage_type = _storage_for_type(_artifact_type)

    return storage_type(artifact_type=_artifact_type, storage_client=storage_client).save_artifact(
        artifact,
        root_uri,
        filename,
    )


def load_record_artifact_from_storage(
    artifact_type: Optional[Union[str, ArtifactStorageType]],
    storage_client: StorageClientType,
    uri: str,
    **kwargs: Any,
) -> Optional[Any]:
    _artifact_type = _get_artifact_storage_type(artifact_type, None)
    storage_type = _storage_for_type(_artifact_type)

    return storage_type(
        artifact_type=_artifact_type,
        storage_client=storage_client,
    ).load_artifact(storage_uri=uri, **kwargs)
