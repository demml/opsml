import shutil
from typing import Any, Dict
from opsml_artifacts.app.routes.models import DownloadModelRequest
from opsml_artifacts import CardRegistry
from opsml_artifacts.registry.cards.cards import ArtifactCard
from opsml_artifacts.registry.sql.registry_base import load_card_from_record
from opsml_artifacts.app.core.config import OpsmlConfig
from opsml_artifacts.registry.sql.records import load_record


def get_real_path(current_path: str, config: OpsmlConfig) -> str:
    new_path = current_path.replace(config.proxy_root, config.STORAGE_URI)
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

    def get_record(self):
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

    def load_card(self, record: Dict[str, Any]) -> ArtifactCard:
        loaded_record = load_record(
            table_name=self.registry.table_name,
            record_data=record,
            storage_client=self.registry.registry.storage_client,
        )

        return load_card_from_record(
            table_name=self.registry.table_name,
            record=loaded_record,
        )
