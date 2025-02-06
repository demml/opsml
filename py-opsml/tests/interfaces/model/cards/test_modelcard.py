from opsml.model import SklearnModel
from opsml.core import SaveKwargs, Tags
from opsml.card import ModelCard, CardType
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
    interface: SklearnModel = random_forest_classifier

    save_path = tmp_path / "test"
    save_path.mkdir()

    tags = Tags()

    tags.add_tag("foo", "bar")
    tags.add_tag("baz", "qux")

    card = ModelCard(
        interface=interface,
        repository="test",
        name="test",
        contact="test",
        to_onnx=True,
        tags=tags,
    )

    card.save(save_path)

    modelcard_json = card.model_dump_json()

    loaded_card = ModelCard.model_validate_json(modelcard_json)

    assert loaded_card.card_type == CardType.Model
    assert loaded_card.interface is None
    loaded_card.interface = SklearnModel()

    # metadata = interface.save(save_path, True)
    # assert metadata.save_metadata.save_kwargs is None


#
# interface.model = None
#
# assert interface.model is None
# assert metadata.save_metadata.data_processor_map.get("preprocessor") is not None
# interface.preprocessor = None
# assert interface.preprocessor is None
#
# interface.load(
#    save_path,
#    model=True,
#    onnx=True,
#    sample_data=True,
# )
#
# assert interface.model is not None
#
# interface.load(
#    save_path,
#    model=False,
#    preprocessor=True,
# )
#
# assert interface.preprocessor is not None
