# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from importlib.metadata import PackageNotFoundError, version

PACKAGE_NAME = "opsml"


def get_version(package_name: str) -> str:
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "unknown"


__version__ = get_version(PACKAGE_NAME)
