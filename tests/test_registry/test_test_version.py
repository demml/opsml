from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import polars as pl
from numpy.typing import NDArray
import pyarrow as pa
from os import path
from unittest.mock import patch
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml.registry.cards.cards import DataCard, RunCard, PipelineCard, ModelCard, DataSplit
from opsml.registry.cards.pipeline_loader import PipelineLoader
from opsml.registry.sql.registry import CardRegistry
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.pipeline import Pipeline
import uuid
from pydantic import ValidationError
from tests.conftest import FOURTEEN_DAYS_TS, FOURTEEN_DAYS_STR


def test_datacard_major_minor_version(db_registries: Dict[str, CardRegistry]):
    # create data card
    registry = db_registries["data"]
    data_card = DataCard(
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        sql_logic={"test": "select * from test_table"},
        version="3.1.1",
    )

    registry.register_card(card=data_card)

    data_card = DataCard(
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3.1",  # specifying major minor version
        sql_logic={"test": "select * from test_table"},
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "3.1.2"

    data_card = DataCard(
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3",  # specifying major with minor bump
        sql_logic={"test": "select * from test_table"},
    )

    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.2.0"

    data_card = DataCard(
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3",  # specifying major with patch bump
        sql_logic={"test": "select * from test_table"},
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "3.2.1"

    data_card = DataCard(
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3.2",  # specifying major minor with minor bump.
        sql_logic={"test": "select * from test_table"},
    )

    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.3.0"

    data_card = DataCard(
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3.2",  # specifying major minor with minor bump.
        sql_logic={"test": "select * from test_table"},
    )

    # This should rarely happen, but should work (3.3.0 already exists, should increment to 3.4.0)
    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.4.0"

    # test initial partial registration
    data_card = DataCard(
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="4.1",  # specifying major minor version
        sql_logic={"test": "select * from test_table"},
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "4.1.0"


def test_pandas_dtypes(db_registries: Dict[str, CardRegistry], drift_dataframe):
    registry = db_registries["data"]
    data, y, _, _ = drift_dataframe

    data["col_11"] = y
    data["eval_flg"] = np.where(data["col_11"] <= 5, 1, 0)
    data["col_11"] = data["col_11"].astype("category")

    datacard = DataCard(
        name="pandas_dtype",
        team="mlops",
        user_email="mlops.com",
        data=data,
        data_splits=[
            DataSplit(label="train", column_value=0, column_name="eval_flg"),
            DataSplit(label="test", column_value=1, column_name="eval_flg"),
        ],
    )
    registry.register_card(card=datacard, version_type="patch")
    datacard = registry.load_card(uid=datacard.uid)
    datacard.load_data()

    splits = datacard.split_data()
    assert splits.train.X.dtypes["col_11"] == "category"
    assert splits.test.X.dtypes["col_11"] == "category"


def test_polars_dtypes(db_registries: Dict[str, CardRegistry], iris_data_polars):
    registry = db_registries["data"]
    data = iris_data_polars

    data = data.with_columns(
        [
            pl.when(pl.col("target") <= 1).then(pl.lit(1)).otherwise(pl.lit(0)).alias("eval_flg"),
            pl.when(pl.col("target") <= 1).then(pl.lit("a")).otherwise(pl.lit("b")).alias("test_cat"),
        ]
    )
    data = data.with_columns(pl.col("test_cat").cast(pl.Categorical))
    orig_schema = data.schema

    datacard = DataCard(
        name="pandas_dtype",
        team="mlops",
        user_email="mlops.com",
        data=data,
        data_splits=[
            DataSplit(label="train", column_value=0, column_name="eval_flg"),
            DataSplit(label="test", column_value=1, column_name="eval_flg"),
        ],
    )
    registry.register_card(card=datacard, version_type="patch")
    datacard = registry.load_card(uid=datacard.uid)
    datacard.load_data()

    splits = datacard.split_data()
    assert splits.train.X.schema["test_cat"] == orig_schema["test_cat"]
    assert splits.test.X.schema["test_cat"] == orig_schema["test_cat"]
