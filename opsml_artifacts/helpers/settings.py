import logging
import os
from typing import IO, Any
import sys
from pythonjsonlogger.jsonlogger import JsonFormatter
from datetime import datetime


class LogFormatter(JsonFormatter):
    """Custom formattero"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.app_env = os.getenv("APP_ENV", "development")

    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("timestamp", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        log_record.setdefault("app_env", self.app_env)


# credit to pyshipt-logging for implementation logic
class ArtifactLogger:
    @classmethod
    def get_handler(cls, stream: IO = sys.stdout) -> logging.StreamHandler:
        log_handler = logging.StreamHandler(stream)
        formatter = LogFormatter()
        log_handler.setFormatter(formatter)
        return log_handler

    @classmethod
    def get_logger(
        cls,
        name: str,
        stream: IO = sys.stdout,
    ):
        log = logging.getLogger(name)
        log.addHandler(cls.get_handler(stream=stream))
        log_level: int = logging.getLevelName("INFO")
        log.setLevel(log_level)
        log.propagate = False

        return log


# class MockSettings(BaseSettings):
#    class Config:
#        arbitrary_types_allowed = True
#        extra = "allow"
#
#
# def get_settings():
#    if bool(os.getenv("ARTIFACT_TESTING_MODE")):
#        from opsml_artifacts.helpers.fixtures.mock_vars import mock_vars
#
#        return MockSettings(**mock_vars)


# might be a better way to do this in the future
# def get_settings():
#    if bool(os.getenv("ARTIFACT_TESTING_MODE")):
#        from opsml_artifacts.helpers.fixtures.mock_vars import mock_vars
#        return MockSettings(**mock_vars)
#    else:
#        if os.getenv("OPMSL_ARTIFACT_ENV").lower() == "gcp":
#
#
#    return GlobalSettings()
#
#
# settings = get_settings()
