from opsml.model import ModelCard, SklearnModel, SaveKwargs
from opsml.data import NumpyData, DataType, PandasData, PolarsData, ArrowData, TorchData
from numpy.typing import NDArray
from pathlib import Path
import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa  # type: ignore
import torch
from typing import List, Dict


def test_save_model_interface(tmp_path: Path, random_forest_classifier: SklearnModel):
    interface = random_forest_classifier

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(save_path, True)
    assert metadata.save_metadata.save_kwargs is None

    interface.model = None

    assert interface.model is None
    assert metadata.save_metadata.data_processor_map.get("preprocessor") is not None
    interface.preprocessor = None
    assert interface.preprocessor is None

    interface.load(
        save_path,
        model=True,
        onnx=True,
        sample_data=True,
    )

    assert interface.model is not None

    interface.load(
        save_path,
        model=False,
        preprocessor=True,
    )

    assert interface.preprocessor is not None
