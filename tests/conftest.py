import os
from sqlalchemy import create_engine
from opsml_artifacts.helpers.settings import SnowflakeParams
from opsml_artifacts.registry.sql.sql_schema import DataSchema, ModelSchema, ExperimentSchema, PipelineSchema
from opsml_artifacts.registry.sql.registry import CardRegistry
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import sessionmaker
import numpy as np
import pandas as pd
import pyarrow as pa


@pytest.fixture(scope="session")
def test_settings():
    from opsml_artifacts.helpers.settings import settings

    return settings


@pytest.fixture(scope="function")
def fake_snowflake_params():
    return SnowflakeParams(
        username="test",
        password="test",
        host="host",
        database="test",
        warehouse="test",
        role="test",
    )


@pytest.fixture(scope="function")
def db_registries():

    url = "sqlite:///:memory:"
    execution_options = {"schema_translate_map": {"ds-artifact-registry": None}}
    engine = create_engine(url=url, execution_options=execution_options)
    mock_session = sessionmaker(bind=engine)
    with patch.multiple(
        "opsml_artifacts.registry.sql.sql_schema.SqlManager",
        _sql_session=mock_session,
        _create_table=MagicMock(return_value=True),
    ):

        DataSchema.__table__.create(bind=engine, checkfirst=True)
        ModelSchema.__table__.create(bind=engine, checkfirst=True)
        ExperimentSchema.__table__.create(bind=engine, checkfirst=True)
        PipelineSchema.__table__.create(bind=engine, checkfirst=True)

        model_registry = CardRegistry(registry_name="model")
        data_registry = CardRegistry(registry_name="data")
        experiment_registry = CardRegistry(registry_name="experiment")
        pipeline_registry = CardRegistry(registry_name="pipeline")

        yield {
            "data": data_registry,
            "model": model_registry,
            "experiment": experiment_registry,
            "pipeline": pipeline_registry,
        }

        # drop tables
        ModelSchema.__table__.drop(bind=engine, checkfirst=True)
        DataSchema.__table__.drop(bind=engine, checkfirst=True)
        ExperimentSchema.__table__.drop(bind=engine, checkfirst=True)
        PipelineSchema.__table__.drop(bind=engine, checkfirst=True)


##### Mocked class as fixtures
@pytest.fixture(scope="session", autouse=True)
def mock_gcsfs():
    with patch.multiple(
        "gcsfs.GCSFileSystem",
        ls=MagicMock(return_value=["gs://test"]),
        upload=MagicMock(return_value=True),
        download=MagicMock(return_value=True),
    ) as mocked_gcsfs:
        yield mocked_gcsfs


######## Data for registry tests


@pytest.fixture(scope="function")
def test_array():
    data = np.random.rand(10, 100)
    return data


@pytest.fixture(scope="function")
def test_split_array():
    indices = np.array([0, 1, 2])
    return [{"label": "train", "indices": indices}]


@pytest.fixture(scope="function")
def test_df():
    df = pd.DataFrame(
        {
            "year": [2020, 2022, 2019, 2021],
            "n_legs": [2, 4, 5, 100],
            "animals": ["Flamingo", "Horse", "Brittle stars", "Centipede"],
        }
    )

    return df


@pytest.fixture(scope="session")
def test_arrow_table():
    n_legs = pa.array([2, 4, 5, 100])
    animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
    names = ["n_legs", "animals"]
    table = pa.Table.from_arrays([n_legs, animals], names=names)
    return table
