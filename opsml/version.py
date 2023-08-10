# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from importlib.metadata import version, PackageNotFoundError


try:
    __version__ = version("opsml")
except PackageNotFoundError:
    __version__ = "unknown"
