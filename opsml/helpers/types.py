# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum


class OpsmlUri(str, Enum):
    STORAGE_URI = "OPSML_STORAGE_URI"
    TRACKING_URI = "OPSML_TRACKING_URI"
    RUN_ID = "OPSML_RUN_ID"


class OpsmlAuth(str, Enum):
    USERNAME = "OPSML_USERNAME"
    PASSWORD = "OPSML_PASSWORD"
