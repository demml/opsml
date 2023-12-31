# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
from numpy.typing import NDArray
from onnx import ModelProto

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.model.interfaces import PyTorchModel
from opsml.registry.types import TorchOnnxArgs, TrainedModelType
from opsml.registry.types.extra import Suffix

logger = ArtifactLogger.get_logger()


class _PytorchArgBuilder:
    def __init__(
        self,
        input_data: Union[NDArray[Any], Dict[str, NDArray[Any]]],
    ):
        self.input_data = input_data

    def _get_input_names(self) -> List[str]:
        if isinstance(self.input_data, dict):
            return list(self.input_data.keys())

        return ["predict"]

    def _get_output_names(self) -> List[str]:
        return ["output"]

    def get_args(self) -> TorchOnnxArgs:
        input_names = self._get_input_names()
        output_names = self._get_output_names()

        return TorchOnnxArgs(
            input_names=input_names,
            output_names=output_names,
        )


class _PyTorchOnnxModel:
    @staticmethod
    def _get_additional_model_args(input_data: Any, onnx_args: Optional[TorchOnnxArgs] = None) -> TorchOnnxArgs:
        """Passes or creates TorchOnnxArgs needed for Onnx model conversion"""

        if onnx_args is None:
            return _PytorchArgBuilder(input_data=input_data).get_args()
        return onnx_args

    @staticmethod
    def convert_to_onnx(self, interface: PyTorchModel, path: Path) -> ModelProto:
        """Converts Pytorch model into Onnx model through torch.onnx.export method"""

        onnx_args = self._get_additional_model_args(
            onnx_args=interface.onnx_args,
            input_data=interface.sample_data,
        )

        # coerce data into tuple or tensor for torch.onnx.export
        if isinstance(interface.sample_data, torch.Tensor):
            arg_data = interface.sample_data

        elif isinstance(interface.sample_data, dict):
            arg_data = tuple(interface.sample_data.values())

        else:
            arg_data = tuple(interface.sample_data)

        save_path = path.with_suffix(Suffix.ONNX.value)
        self.trained_model.eval()  # force model into evaluation mode

        # export to file
        torch.onnx.export(
            model=self.trained_model,
            args=arg_data,
            f=save_path.as_posix(),
            **onnx_args.model_dump(exclude={"options"}),
        )

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts a tensorflow keras model"""

        onnx_model = self._get_onnx_model()

        return onnx_model

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class == TrainedModelType.PYTORCH
