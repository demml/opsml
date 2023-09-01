from typing import Any, cast, Dict, Tuple

import os
import sys

import pandas as pd
from numpy.typing import NDArray
import pytest
from sklearn import pipeline
import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import shutil
from opsml.registry import DataCard, ModelCard
from opsml.registry.cards.types import CardInfo
from opsml.projects.mlflow import MlflowProject, ProjectInfo, MlflowActiveRun
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.types import ImageDataset
from tests import conftest
import matplotlib
import torch

matplotlib.use("Agg")

logger = ArtifactLogger.get_logger(__name__)


def test_mlflow_image_dataset(mlflow_project: MlflowProject, sklearn_pipeline) -> None:
    """verify we can save image dataset"""

    with mlflow_project.run() as run:
        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        run.register_card(card=data_card, version_type="major")

        # Create metrics / params / cards
        image_dataset = ImageDataset(
            image_dir="tests/assets/image_dataset",
            metadata="metadata.json",
        )

        data_card = DataCard(
            data=image_dataset,
            name="image_test",
            team="mlops",
            user_email="mlops.com",
        )

        run.register_card(card=data_card)
        loaded_card = run.load_card(registry_name="data", info=CardInfo(uid=data_card.uid))
        loaded_card.data.image_dir = "test_image_dir"
        loaded_card.load_data()

        assert os.path.isdir(loaded_card.data.image_dir)
        meta_path = os.path.join(loaded_card.data.image_dir, loaded_card.data.metadata)
        assert os.path.exists(meta_path)
