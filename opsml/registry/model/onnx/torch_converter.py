# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import tempfile
from typing import Any, Dict, List, Optional, Union, cast

from numpy.typing import NDArray
from onnx import ModelProto

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.model.interfaces import PyTorchModel
from opsml.registry.model.utils.data_helper import ModelDataHelper
from opsml.registry.types import TorchOnnxArgs, TrainedModelType

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
    def __init__(self, model_interface: PyTorchModel, data_helper: ModelDataHelper):
        model_interface.onnx_args = self._get_additional_model_args(
            onnx_args=model_interface.onnx_args,
            input_data=data_helper.data,
        )
        super().__init__(model_interface=model_interface, data_helper=data_helper)

    @property
    def interface(self) -> PyTorchModel:
        return cast(PyTorchModel, self._interface)

    def _get_additional_model_args(
        self,
        input_data: Any,
        onnx_args: Optional[TorchOnnxArgs] = None,
    ) -> TorchOnnxArgs:
        """Passes or creates TorchOnnxArgs needed for Onnx model conversion"""

        if onnx_args is None:
            return _PytorchArgBuilder(input_data=input_data).get_args()
        return onnx_args

    def _get_onnx_model(self) -> ModelProto:
        """Converts Pytorch model into Onnx model through torch.onnx.export method"""

        import torch

        assert isinstance(self.interface.onnx_args, TorchOnnxArgs)

        # coerce data into tuple or tensor for torch.onnx.export
        if isinstance(self.data_helper.data, torch.Tensor):
            arg_data = self.data_helper.data

        elif isinstance(self.data_helper.data, dict):
            arg_data = tuple(self.data_helper.data.values())

        else:
            arg_data = tuple(self.data_helper.data)

        with tempfile.TemporaryDirectory() as tmp_dir:
            filename = f"{tmp_dir}/model.onnx"
            self.trained_model.eval()  # force model into evaluation mode
            torch.onnx.export(
                model=self.trained_model,
                args=arg_data,
                f=filename,
                **self.interface.onnx_args.model_dump(exclude={"options"}),
            )

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts a tensorflow keras model"""

        onnx_model = self._get_onnx_model()

        return onnx_model

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class == TrainedModelType.PYTORCH
