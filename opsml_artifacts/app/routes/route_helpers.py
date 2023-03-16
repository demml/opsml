from typing import Any, Dict

from opsml_artifacts.app.core.config import OpsmlConfig


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
