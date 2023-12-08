import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from opsml.helpers.types import OpsmlUri
from opsml.registry.utils.settings import settings


class Tags(str, Enum):
    NAME = "name"
    TEAM = "team"
    EMAIL = "user_email"
    VERSION = "version"
