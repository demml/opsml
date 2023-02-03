# pylint: disable=import-outside-toplevel

from datetime import datetime
import os
from typing import Any, Dict
from pydantic import root_validator, BaseSettings
from enum import Enum
import sys
import logging

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class MockSettings(BaseSettings):
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


def get_settings():
    if bool(os.getenv("ARTIFACT_TESTING_MODE")):
        from opsml_artifacts.helpers.fixtures.mock_vars import mock_vars

        return MockSettings(**mock_vars)


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
