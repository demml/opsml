import shutil
from pathlib import Path
from typing import Any, Dict, cast

from opsml.app.core.config import OpsmlConfig
from opsml.app.routes.models import DownloadModelRequest
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import clean_string
from opsml.registry import CardRegistry, ModelCard
from opsml.registry.cards.cards import ArtifactCard
from opsml.registry.model.types import ModelApiDef
from opsml.registry.sql.records import load_record
from opsml.registry.sql.registry_base import load_card_from_record
from opsml.registry.storage.storage_system import StorageClientType
from streaming_form_data.targets import FileTarget

logger = ArtifactLogger.get_logger(__name__)

BASE_SAVE_PATH = "app"
MODEL_FILE = "model_def.json"


def get_real_path(current_path: str, proxy_root: str, storage_root: str) -> str:
    new_path = current_path.replace(proxy_root, f"{storage_root}/")
    return new_path


def replace_proxy_root(
    record: Dict[str, Any],
    storage_root: str,
    proxy_root: str,
) -> Dict[str, Any]:

    for name, value in record.items():
        if "uri" in name:
            if isinstance(value, str):
                real_path = get_real_path(
                    current_path=value,
                    proxy_root=proxy_root,
                    storage_root=storage_root,
                )
                record[name] = real_path

        if isinstance(value, dict):
            replace_proxy_root(
                record=value,
                storage_root=storage_root,
                proxy_root=proxy_root,
            )

    return record


def delete_dir(dir_path: str):
    """Deletes a file"""

    try:
        shutil.rmtree(dir_path)
    except Exception as error:  # pylint: disable=broad-except
        raise ValueError(f"Failed to delete {dir_path}. {error}") from error


class ModelDownloader:
    def __init__(
        self,
        registry: CardRegistry,
        model_info: DownloadModelRequest,
        config: OpsmlConfig,
    ):
        self.registry = registry
        self.model_info = model_info
        self.config = config
        self.base_path = BASE_SAVE_PATH
        self.clean_info()

    @property
    def file_path(self) -> str:
        return str(self._file_path)

    @file_path.setter
    def file_path(self, file_path: str):
        self._file_path = file_path

    def clean_info(self):
        self.model_info.name = clean_string(self.model_info.name)
        self.model_info.team = clean_string(self.model_info.team)

    def get_record(self) -> Dict[str, Any]:
        record = self.registry.registry.list_cards(
            uid=self.model_info.uid,
            name=self.model_info.name,
            team=self.model_info.team,
            version=self.model_info.version,
        )

        if len(record) < 1:
            raise ValueError("No model record found. Please check api parameters")

        return replace_proxy_root(
            record=record[0],  # only 1 record should be returned
            storage_root=self.config.STORAGE_URI,
            proxy_root=self.config.proxy_root,
        )

    def load_card(self) -> ArtifactCard:
        raw_record = self.get_record()

        loaded_record = load_record(
            table_name=self.registry.table_name,
            record_data=raw_record,
            storage_client=self.registry.registry.storage_client,
        )

        return load_card_from_record(
            table_name=self.registry.table_name,
            record=loaded_record,
        )

    def _get_model_api_def(self, model_card: ModelCard) -> ModelApiDef:
        onnx_model = model_card.onnx_model(start_onnx_runtime=False)
        api_model = onnx_model.get_api_model()

        return api_model

    def load_model_def(self) -> ModelApiDef:
        model_card = self.load_card()
        return self._get_model_api_def(model_card=cast(ModelCard, model_card))

    def _set_path(self, api_def: ModelApiDef) -> Path:
        path = Path(f"{self.base_path}/onnx_model/{self.model_info.name}/v{api_def.model_version}/")
        path.mkdir(parents=True, exist_ok=True)
        return path / MODEL_FILE

    def _write_api_json(self, api_def: ModelApiDef, filepath: Path) -> None:

        with filepath.open("w", encoding="utf-8") as file_:
            file_.write(api_def.json())
        logger.info("Saved api model def to %s", filepath)

    def _save_api_def(self, api_def: ModelApiDef):
        if self.model_info.name is None:
            self.model_info.name = api_def.model_name

        filepath = self._set_path(api_def=api_def)
        self._write_api_json(api_def=api_def, filepath=filepath)
        path = filepath.absolute().as_posix()
        self.file_path = path

    def download_model(self) -> None:
        api_def = self.load_model_def()
        self._save_api_def(api_def=api_def)


def iterfile(file_path: str, chunk_size: int):
    with open(file_path, "rb") as file_:
        while chunk := file_.read(chunk_size):
            yield chunk


class MaxBodySizeException(Exception):
    def __init__(self, body_len: str):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)


class ExternalFileTarget(FileTarget):
    def __init__(
        self,
        filename: str,
        storage_client: StorageClientType,
        allow_overwrite: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(filename=filename, allow_overwrite=allow_overwrite, *args, **kwargs)

        self.storage_client = fs

    def on_start(self):
        self._fd = self.storage_client.open(self.filename, self._mode)
