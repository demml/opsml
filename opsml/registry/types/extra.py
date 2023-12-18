# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum


class CommonKwargs(str, Enum):
    IS_PIPELINE = "is_pipeline"
    MODEL_TYPE = "model_type"
    MODEL_CLASS = "model_class"
    MODEL_ARCH = "model_arch"
    PREPROCESSOR_NAME = "preprocessor_name"
    PREPROCESSOR = "preprocessor"
    TASK_TYPE = "task_type"
    MODEL = "model"
    UNDEFINED = "undefined"
    BACKEND = "backend"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SAMPLE_DATA = "sample_data"
