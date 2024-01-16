# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
from typing import List, Tuple, Union, cast

import onnx
import onnxruntime as rt
import torch

from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.pytorch import TorchModel, ValidData
from opsml.model.interfaces.pytorch_lightning import LightningModel
from opsml.types import OnnxModel, TorchOnnxArgs

logger = ArtifactLogger.get_logger()


class _PytorchArgBuilder:
    def __init__(self, input_data: ValidData):
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
    def __init__(self, model_interface: TorchModel):
        self.interface = model_interface

    def _get_additional_model_args(self) -> TorchOnnxArgs:
        """Passes or creates TorchOnnxArgs needed for Onnx model conversion"""

        if self.interface.onnx_args is None:
            assert self.interface.sample_data is not None, "Sample data must be provided"
            return _PytorchArgBuilder(input_data=self.interface.sample_data).get_args()
        return self.interface.onnx_args

    def _coerce_data_for_onnx(self) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        assert self.interface.sample_data is not None, "Sample data must not be None"

        if isinstance(self.interface.sample_data, dict):
            return tuple(self.interface.sample_data.values())
        if isinstance(self.interface.sample_data, torch.Tensor):
            return self.interface.sample_data
        return tuple(self.interface.sample_data)

    def _load_onnx_model(self, path: Path) -> rt.InferenceSession:
        return rt.InferenceSession(
            path_or_bytes=path,
            providers=rt.get_available_providers(),
        )

    def convert_to_onnx(self, path: Path) -> OnnxModel:
        """Converts Pytorch model into Onnx model through torch.onnx.export method"""

        logger.info("Staring conversion of PyTorch model to ONNX")

        assert self.interface.model is not None, "Model must not be None"

        arg_data = self._coerce_data_for_onnx()
        onnx_args = self._get_additional_model_args()
        # export
        self.interface.model.eval()  # force model into evaluation mode
        torch.onnx.export(
            model=self.interface.model,
            args=arg_data,
            f=path.as_posix(),
            **onnx_args.model_dump(exclude={"options"}),
        )

        # load
        return OnnxModel(
            onnx_version=onnx.__version__,  # type: ignore[attr-defined]
            sess=self._load_onnx_model(path=path),
        )


class _PyTorchLightningOnnxModel(_PyTorchOnnxModel):
    def __init__(self, model_interface: LightningModel):
        super().__init__(model_interface=model_interface)

        self.interface = model_interface

    def _get_additional_model_args(self) -> TorchOnnxArgs:
        """Passes or creates TorchOnnxArgs needed for Onnx model conversion"""

        if self.interface.onnx_args is None:
            assert self.interface.sample_data is not None, "No sample data provided"
            return _PytorchArgBuilder(input_data=cast(ValidData, self.interface.sample_data)).get_args()
        return self.interface.onnx_args

    def _load_onnx_model(self, path: Path) -> rt.InferenceSession:
        return rt.InferenceSession(
            path_or_bytes=path,
            providers=rt.get_available_providers(),
        )

    def convert_to_onnx(self, path: Path) -> OnnxModel:
        """Converts Pytorch model into Onnx model through torch.onnx.export method"""

        logger.info("Staring conversion of PyTorch Lightning model to ONNX")

        assert self.interface.model is not None, "Trainer must not be None"
        assert self.interface.model.model is not None, "Model must not be None"

        onnx_args = self._get_additional_model_args()

        self.interface.model.model.to_onnx(
            path.as_posix(),
            self.interface.sample_data,
            **onnx_args.model_dump(exclude={"options"}),
        )

        # load
        return OnnxModel(
            onnx_version=onnx.__version__,  # type: ignore[attr-defined]
            sess=self._load_onnx_model(path=path),
        )
