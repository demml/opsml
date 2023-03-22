import shutil
from pathlib import Path
from typing import Any, Dict, cast

from opsml_artifacts import CardRegistry, ModelCard
from opsml_artifacts.app.core.config import OpsmlConfig
from opsml_artifacts.app.routes.models import DownloadModelRequest
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.cards import ArtifactCard
from opsml_artifacts.registry.model.types import ModelApiDef
from opsml_artifacts.registry.sql.records import load_record
from opsml_artifacts.registry.sql.registry_base import load_card_from_record

logger = ArtifactLogger.get_logger(__name__)

BASE_SAVE_PATH = "app"
MODEL_FILE = "model_def.json"


def get_real_path(current_path: str, config: OpsmlConfig) -> str:
    new_path = current_path.replace(config.proxy_root, f"{config.STORAGE_URI}/")
    return new_path


def switch_out_proxy_location(
    record: Dict[str, Any],
    config: OpsmlConfig,
) -> Dict[str, Any]:

    for name, value in record.items():
        if "uri" in name:
            if isinstance(value, str):
                real_path = get_real_path(current_path=value, config=config)
                record[name] = real_path
            if isinstance(value, dict):
                for nested_name, nested_value in value.items():
                    real_path = get_real_path(current_path=nested_value, config=config)
                    value[nested_name] = real_path
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

    @property
    def file_path(self) -> str:
        return str(self._file_path)

    @file_path.setter
    def file_path(self, file_path: str):
        self._file_path = file_path

    def get_record(self) -> Dict[str, Any]:
        record = self.registry.registry.list_cards(
            uid=self.model_info.uid,
            name=self.model_info.name,
            team=self.model_info.team,
            version=self.model_info.version,
        )[0]

        return switch_out_proxy_location(
            record=record,
            config=self.config,
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
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk
