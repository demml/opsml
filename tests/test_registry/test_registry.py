import os
import sys
import uuid
from pathlib import Path
from typing import Tuple

import joblib
import polars as pl
import pytest
from pytest_lazyfixture import lazy_fixture
from sqlalchemy import select

from opsml.cards import (
    DataCard,
    DataCardMetadata,
    Description,
    ModelCard,
    PipelineCard,
    RunCard,
)
from opsml.data import (
    ArrowData,
    DataInterface,
    NumpyData,
    PandasData,
    PolarsData,
    SqlData,
)
from opsml.helpers.exceptions import VersionError
from opsml.model import ModelInterface, SklearnModel
from opsml.registry import CardRegistries
from opsml.registry.records import registry_name_record_map
from opsml.registry.sql.base.query_engine import DialectHelper
from opsml.registry.sql.base.sql_schema import DataSchema
from tests.conftest import FOURTEEN_DAYS_STR, FOURTEEN_DAYS_TS, OPSML_TRACKING_URI


def test_registry_dialect(db_registries: CardRegistries):
    # Pick one registry as they all have the same engine

    registry = db_registries.data

    if "postgres" in OPSML_TRACKING_URI:
        assert "postgres" in registry._registry.engine.dialect

    elif "mysql" in OPSML_TRACKING_URI:
        assert "mysql" in registry._registry.engine.dialect

    elif "sqlite" in OPSML_TRACKING_URI:
        assert "sqlite" in registry._registry.engine.dialect
    else:
        raise ValueError("Supported dialect not found")


@pytest.mark.parametrize(
    "test_interface",
    [
        lazy_fixture("numpy_data"),
        lazy_fixture("pandas_data"),
        lazy_fixture("polars_data"),
        lazy_fixture("arrow_data"),
    ],
)
def test_register_data(
    db_registries: CardRegistries,
    test_interface: tuple[NumpyData, ArrowData, PandasData, PolarsData],
):
    # create data card
    registry = db_registries.data

    data_card = DataCard(
        interface=test_interface,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )

    registry.register_card(card=data_card)

    # test idempotency
    version = data_card.version
    registry.register_card(card=data_card)
    assert data_card.version == version

    cards = registry.list_cards(name=data_card.name, repository=data_card.repository)
    assert bool(cards)

    cards = registry.list_cards(name=data_card.name)
    assert bool(cards)

    cards = registry.list_cards()
    assert bool(cards)

    cards = registry.list_cards(name=data_card.name, repository=data_card.repository, version="1.0.0")
    assert bool(cards)

    data_card = DataCard(
        interface=test_interface,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )
    registry.register_card(card=data_card)

    cards = registry.list_cards(name=data_card.name, repository=data_card.repository, version="^1")
    assert len(cards) >= 1

    # Verify card name normalization (replacing "_" with "-")
    names = registry._registry.get_unique_card_names(repository="mlops")
    # NOTE: opsml replaces "_" with "-" in card name name
    assert "test-df" in names

    names = registry._registry.get_unique_card_names()
    assert "test-df" in names

    assert "mlops" in registry._registry.unique_repositories


def test_datacard_sql_register(sql_data: SqlData, db_registries: CardRegistries):
    # create data card
    registry = db_registries.data
    data_card = DataCard(
        interface=sql_data,
        name="test_sql",
        repository="mlops",
        contact="mlops.com",
        metadata=DataCardMetadata(
            description=Description(summary="data_readme.md"),
        ),
    )
    data_card.add_tag("test", "hello")

    registry.register_card(card=data_card)
    loaded_card: DataCard = registry.load_card(uid=data_card.uid)
    assert loaded_card.interface.sql_logic.get("test") is not None
    assert data_card.name == "test-sql"
    assert data_card.repository == "mlops"
    assert data_card.version >= "1.0.0"
    assert data_card.tags == {"test": "hello"}

    cards = registry.list_cards(
        uid=data_card.uid,
        tags={"test": "hello"},
    )
    assert cards[0]["tags"] == {"test": "hello"}


def test_datacard_sql_register_date(sql_data: SqlData, db_registries: CardRegistries):
    # create data card at current time
    registry = db_registries.data
    data_card = DataCard(
        interface=sql_data,
        name="test_sql",
        repository="mlops",
        contact="mlops.com",
    )

    registry.register_card(card=data_card)
    record = registry_name_record_map[data_card.card_type](**data_card.create_registry_record())

    # add card with a timestamp from 14 days ago
    record.timestamp = FOURTEEN_DAYS_TS
    registry._registry.update_card_record(record.model_dump())

    cards = registry.list_cards()
    assert len(cards) >= 1

    cards = registry.list_cards(max_date=FOURTEEN_DAYS_STR)
    assert len(cards) >= 1


def test_datacard_sql_register_file(sql_file: SqlData, db_registries: CardRegistries):
    # create data card
    registry = db_registries.data
    data_card = DataCard(
        interface=sql_file,
        name="test_file",
        repository="mlops",
        contact="mlops.com",
    )
    registry.register_card(card=data_card)
    loaded_card = registry.load_card(uid=data_card.uid)
    assert loaded_card.interface.sql_logic.get("test") == "SELECT ORDER_ID FROM TEST_TABLE limit 100"


def test_unique_name_fail(sql_file: SqlData, db_registries: CardRegistries):
    # create data card
    registry = db_registries.data
    data_card = DataCard(
        interface=sql_file,
        name="test_name_fail",
        repository="mlops",
        contact="mlops.com",
    )

    registry.register_card(card=data_card)

    # test registering card with same name and different repository
    with pytest.raises(ValueError):
        data_card = DataCard(
            interface=sql_file,
            name="test_name_fail",
            repository="fail_repositories",
            contact="mlops.com",
        )

        registry.register_card(card=data_card)


def test_semver_registry_list(
    numpy_data: NumpyData,
    db_registries: CardRegistries,
):
    # create data card
    registry = db_registries.data

    # version 1
    for i in range(0, 5):
        data_card = DataCard(
            interface=numpy_data,
            name="test_semver",
            repository="mlops",
            contact="mlops.com",
        )
        registry.register_card(card=data_card, version_type="patch")

    cards = registry.list_cards(name="test_semver", repository="mlops", version="^1.0.0")

    assert len(cards) == 1
    assert cards[0]["version"] == "1.0.4"

    # version 2
    data_card = DataCard(
        interface=numpy_data,
        name="test_semver",
        repository="mlops",
        contact="mlops.com",
    )
    registry.register_card(card=data_card, version_type="major")

    for i in range(0, 12):
        data_card = DataCard(
            interface=numpy_data,
            name="test_semver",
            repository="mlops",
            contact="mlops.com",
        )
        registry.register_card(card=data_card)

    # should return 13 versions
    cards = registry.list_cards(name=data_card.name, repository=data_card.repository, version="2.*.*")
    assert len(cards) == 13

    cards = registry.list_cards(name=data_card.name, repository=data_card.repository, version="^2.0.0")
    cards[0]["version"] == "2.12.0"
    assert len(cards) == 1

    # pre-release
    data_card_pre = DataCard(
        interface=numpy_data,
        name="test_semver",
        repository="mlops",
        contact="mlops.com",
        version="3.0.0-rc.1",
    )
    registry.register_card(card=data_card_pre)

    records = registry.list_cards(name=data_card.name, repository=data_card.repository, version="3.*.*")

    assert len(records) == 1

    data_card_pre.version = "3.0.0"
    registry.update_card(card=data_card_pre)

    # check update works
    records = registry.list_cards(name=data_card.name, repository=data_card.repository, version="3.*.*")

    assert records[0]["version"] == "3.0.0"

    with pytest.raises(VersionError):
        # try registering card where version already exists
        data_card = DataCard(
            interface=numpy_data,
            name="test_semver",
            repository="mlops",
            contact="mlops.com",
            version="3.0.0-rc.1",  # cant create a release for a minor version that already exists
        )
        registry.register_card(card=data_card)

    with pytest.raises(ValueError):
        # try invalid semver
        data_card = DataCard(
            interface=numpy_data,
            name="test_semver",
            repository="mlops",
            contact="mlops.com",
            version="3.0.0blah",
        )
        registry.register_card(card=data_card)

    # pre-release
    data_card_pre = DataCard(
        interface=numpy_data,
        name="test_semver",
        repository="mlops",
        contact="mlops.com",
        version="3.0.1-rc.1",
    )
    registry.register_card(card=data_card_pre)

    # test patch semver sort
    for i in range(0, 5):
        data_card = DataCard(
            interface=numpy_data,
            name="patch",
            repository="mlops",
            contact="mlops.com",
        )
        registry.register_card(card=data_card, version_type="patch")

    cards = registry.list_cards(name="patch", repository="mlops", version="^1.0.0")

    assert cards[0]["version"] == "1.0.4"


def test_runcard(
    linear_regression: Tuple[ModelInterface, NumpyData],
    db_registries: CardRegistries,
):
    registry = db_registries.run
    model, _ = linear_regression

    run = RunCard(
        name="test_run",
        repository="mlops",
        contact="mlops.com",
        datacard_uids=["test_uid"],
    )
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})
    assert run.get_metric("test_metric").value == 10
    assert run.get_metric("test_metric2").value == 20

    # log artifact from file
    name = uuid.uuid4().hex
    save_path = f"tests/assets/{name}.joblib"
    joblib.dump(model.model, save_path)
    run.log_artifact_from_file("linear_reg", save_path)
    assert run.artifact_uris.get("linear_reg") is not None
    os.remove(save_path)

    # register and load card
    registry.register_card(card=run)
    loaded_card: RunCard = registry.load_card(uid=run.uid)

    loaded_card.load_artifacts("linear_reg")
    assert Path(loaded_card.artifact_uris.get("linear_reg").local_path).exists()
    os.remove(loaded_card.artifact_uris.get("linear_reg").local_path)
    assert loaded_card.uid == run.uid
    assert loaded_card.get_metric("test_metric").value == 10
    assert loaded_card.get_metric("test_metric2").value == 20

    with pytest.raises(ValueError):
        loaded_card.get_metric("test")

    with pytest.raises(ValueError):
        loaded_card.get_parameter("test")

    # metrics take floats, ints
    with pytest.raises(ValueError):
        loaded_card.log_metric("test_fail", "10")

    # params take floats, ints, str
    with pytest.raises(ValueError):
        loaded_card.log_parameter("test_fail", model.model)

    # test updating
    loaded_card.log_metric("updated_metric", 20)
    registry.update_card(card=loaded_card)

    # should be same runid
    loaded_card = registry.load_card(uid=run.uid)
    assert loaded_card.get_metric("updated_metric").value == 20


def test_model_registry_onnx(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[ModelInterface, DataInterface],
):
    # create data card
    data_registry = db_registries.data
    model, data = sklearn_pipeline

    data_card = DataCard(
        interface=data,
        name="pipeline_data",
        repository="mlops",
        contact="mlops.com",
    )
    data_registry.register_card(card=data_card)

    # test onnx
    model_card = ModelCard(
        interface=model,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry = db_registries.model
    model_registry.register_card(card=model_card)

    loaded_card: ModelCard = model_registry.load_card(uid=model_card.uid)
    assert isinstance(loaded_card.interface, SklearnModel)

    loaded_card: ModelCard = db_registries.model.load_card(uid=model_card.uid)

    assert loaded_card != model_card
    assert loaded_card.interface.model is None
    assert loaded_card.interface.sample_data is None
    assert loaded_card.interface.onnx_model is None

    loaded_card.load_model()
    loaded_card.load_onnx_model()

    assert loaded_card.interface.model is not None
    assert loaded_card.interface.sample_data is not None
    assert loaded_card.interface.onnx_model is not None

    # test no onnx
    model_card = ModelCard(
        interface=model,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=data_card.uid,
    )

    model_registry = db_registries.model
    model_registry.register_card(card=model_card)

    loaded_card: ModelCard = model_registry.load_card(uid=model_card.uid)
    assert isinstance(loaded_card.interface, SklearnModel)


def test_modelcard_register_fail(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[ModelInterface, DataInterface],
):
    model_registry = db_registries.model
    model, _ = sklearn_pipeline

    model_card = ModelCard(
        interface=model,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=None,
    )

    with pytest.raises(ValueError):
        model_registry.register_card(card=model_card)


def test_load_data_card(pandas_data: PandasData, db_registries: CardRegistries):
    data_name = "test_df"
    repository = "mlops"
    contact = "mlops.com"

    registry = db_registries.data
    data: PandasData = pandas_data

    data_card = DataCard(
        interface=data,
        name=data_name,
        repository=repository,
        contact=contact,
        metadata=DataCardMetadata(
            additional_info={"input_metadata": 20},
            description=Description(summary="test description"),
        ),
    )

    data_card.add_info(info={"added_metadata": 10})
    registry.register_card(card=data_card)

    loaded_data: DataCard = registry.load_card(name=data_name, version=data_card.version)

    loaded_data.load_data()

    assert int(loaded_data.metadata.additional_info["input_metadata"]) == 20
    assert int(loaded_data.metadata.additional_info["added_metadata"]) == 10
    assert loaded_data.metadata.description.summary == "test description"
    assert isinstance(loaded_data.interface.dependent_vars[0], int)
    assert isinstance(loaded_data.interface.dependent_vars[1], str)
    assert loaded_data.interface.sql_logic["test"] == "SELECT * FROM TEST_TABLE"

    assert loaded_data.interface.data_splits == data.data_splits

    # update
    loaded_data.version = "1.2.0"
    registry.update_card(card=loaded_data)

    record = registry.query_value_from_card(uid=loaded_data.uid, columns=["version", "timestamp"])
    assert record["version"] == "1.2.0"


def test_datacard_failure(pandas_data: PandasData, db_registries: CardRegistries):
    data_name = "test_df"
    repository = "mlops"
    contact = "mlops.com"

    data_registry = db_registries.data
    data: PandasData = pandas_data

    # remove attr
    data.data = None
    data.sql_logic = {}

    # should fail: data nor sql are provided
    with pytest.raises(ValueError) as ve:
        datacard = DataCard(
            interface=data,
            name=data_name,
            repository=repository,
            contact=contact,
            metadata=DataCardMetadata(additional_info={"input_metadata": 20}),
            dependent_vars=[200, "test"],
        )
        data_registry.register_card(card=datacard)

    assert ve.match("DataInterface must have data or sql logic")


def test_pipeline_registry(db_registries: CardRegistries):
    pipeline_card = PipelineCard(
        name="test_df",
        repository="mlops",
        contact="mlops.com",
        pipeline_code_uri="test_pipe_uri",
    )
    for card_type in ["data", "run", "model"]:
        pipeline_card.add_card_uid(uid=uuid.uuid4().hex, card_type=card_type)

    # register
    registry = db_registries.pipeline
    registry.register_card(card=pipeline_card)
    loaded_card: PipelineCard = registry.load_card(uid=pipeline_card.uid)
    loaded_card.add_card_uid(uid="updated_uid", card_type="data")
    registry.update_card(card=loaded_card)
    registry.list_cards(uid=loaded_card.uid)
    values = registry.query_value_from_card(
        uid=loaded_card.uid,
        columns=["datacard_uids"],
    )
    assert bool(values["datacard_uids"])

    with pytest.raises(ValueError) as ve:
        registry.delete_card(card=loaded_card)
    assert ve.match("PipelineCardRegistry does not support delete_card")


def test_full_pipeline_with_loading(
    linear_regression: Tuple[SklearnModel, NumpyData],
    db_registries: CardRegistries,
):
    repository = "mlops"
    contact = "mlops.com"
    pipeline_code_uri = "test_pipe_uri"
    data_registry = db_registries.data
    model_registry = db_registries.model
    run_registry = db_registries.run
    pipeline_registry = db_registries.pipeline
    model, data = linear_regression

    #### Create DataCard
    data_card = DataCard(
        interface=data,
        name="test_data",
        repository=repository,
        contact=contact,
    )

    data_registry.register_card(card=data_card)
    ###### ModelCard
    model_card = ModelCard(
        interface=model,
        name="test_model",
        repository=repository,
        contact=contact,
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry.register_card(model_card)

    ##### RunCard
    exp_card = RunCard(
        name="test_experiment",
        repository=repository,
        contact=contact,
        datacard_uids=[data_card.uid],
        modelcard_uids=[model_card.uid],
    )
    exp_card.log_metric("test_metric", 10)
    run_registry.register_card(card=exp_card)

    #### PipelineCard
    pipeline_card = PipelineCard(
        name="test_pipeline",
        repository=repository,
        contact=contact,
        pipeline_code_uri=pipeline_code_uri,
        datacard_uids=[data_card.uid],
        modelcard_uids=[model_card.uid],
        runcard_uids=[exp_card.uid],
    )
    pipeline_registry.register_card(card=pipeline_card)


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_model_registry_with_polars(
    db_registries: CardRegistries,
    linear_regression_polars: Tuple[SklearnModel, PolarsData],
):
    # create data card
    data_registry = db_registries.data
    model, data = linear_regression_polars
    data_card = DataCard(
        interface=data,
        name="polars_data",
        repository="mlops",
        contact="mlops.com",
    )
    data_registry.register_card(card=data_card)

    model_card = ModelCard(
        interface=model,
        name="polars_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry = db_registries.model
    model_registry.register_card(card=model_card)

    model_registry.load_card(uid=model_card.uid)


def test_pandas_dtypes(db_registries: CardRegistries, pandas_data: PandasData):
    registry = db_registries.data

    pandas_data.data["animals"] = pandas_data.data["animals"].astype("category")
    datacard = DataCard(
        name="pandas_dtype",
        repository="mlops",
        contact="mlops.com",
        interface=pandas_data,
    )

    registry.register_card(card=datacard, version_type="patch")
    datacard: DataCard = registry.load_card(uid=datacard.uid)
    datacard.load_data()

    splits = datacard.interface.split_data()
    assert splits.train.X.dtypes["animals"] == "category"
    assert splits.test.X.dtypes["animals"] == "category"


def test_polars_dtypes(db_registries: CardRegistries, iris_data_polars: PolarsData):
    registry = db_registries.data
    data = iris_data_polars.data

    new_data = data.with_columns(
        [
            pl.when(pl.col("target") <= 1).then(pl.lit(1)).otherwise(pl.lit(0)).alias("eval_flg"),
            pl.when(pl.col("target") <= 1).then(pl.lit("a")).otherwise(pl.lit("b")).alias("test_cat"),
        ]
    )
    new_data = new_data.with_columns(pl.col("test_cat").cast(pl.Categorical))
    orig_schema = new_data.schema

    iris_data_polars.data = new_data

    datacard = DataCard(
        name="pandas_dtype",
        repository="mlops",
        contact="mlops.com",
        interface=iris_data_polars,
    )
    registry.register_card(card=datacard, version_type="patch")
    datacard = registry.load_card(uid=datacard.uid)
    datacard.load_data()

    splits = datacard.interface.split_data()
    assert splits.train.X.schema["test_cat"] == orig_schema["test_cat"]
    assert splits.test.X.schema["test_cat"] == orig_schema["test_cat"]


def _test_datacard_major_minor_version(sql_data: SqlData, db_registries: CardRegistries):
    # create data card
    registry = db_registries.data
    data_card = DataCard(
        interface=sql_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3.1.1",
    )

    registry.register_card(card=data_card)

    data_card = DataCard(
        interface=sql_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3.1",  # specifying major minor version
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "3.1.2"

    data_card = DataCard(
        interface=sql_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3",  # specifying major with minor bump
    )

    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.2.0"

    data_card = DataCard(
        interface=sql_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3",  # specifying major with patch bump
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "3.2.1"

    data_card = DataCard(
        interface=sql_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3.2",  # specifying major minor with minor bump.
    )

    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.3.0"

    data_card = DataCard(
        interface=sql_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3.2",  # specifying major minor with minor bump.
    )

    # This should rarely happen, but should work (3.3.0 already exists, should increment to 3.4.0)
    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.4.0"

    # test initial partial registration
    data_card = DataCard(
        interface=sql_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="4.1",  # specifying major minor version
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "4.1.0"


def test_list_cards(db_registries: CardRegistries):
    data_reg = db_registries.data

    record = {
        "uid": uuid.uuid4().hex,
        "timestamp": 1,
        "name": "list-test",
        "repository": "test_repository",
        "contact": "test_email",
        "version": "1.0.0",
        "data_type": "test_type",
    }

    for i in range(1, 25):
        record["uid"] = uuid.uuid4().hex

        if i > 20:
            record["version"] = f"20.{i}.4"
        else:
            record["version"] = f"1.{i}.100"

        with data_reg._registry.engine.session() as sess:
            sess.add(DataSchema(**record))
            sess.commit()

    # add rc
    record["uid"] = uuid.uuid4().hex
    record["version"] = "1.15.0-rc.1"

    with data_reg._registry.engine.session() as sess:
        sess.add(DataSchema(**record))
        sess.commit()

    cards = data_reg.list_cards(name="list-test", limit=5)
    assert cards[0]["version"] == "20.24.4"
    assert cards[1]["version"] == "20.23.4"
    assert cards[4]["version"] == "1.20.100"


def test_sql_version_logic():
    """This is more to ensure coverage. Postgres and Mysql have been tested offline"""

    select_query = select(DataSchema)

    # postgres
    query = DialectHelper.get_dialect_logic(select_query, DataSchema, "postgres")
    assert all((col in query.columns.keys() for col in ["major", "minor", "patch"]))

    # mysql
    query = DialectHelper.get_dialect_logic(select_query, DataSchema, "mysql")
    assert all((col in query.columns.keys() for col in ["major", "minor", "patch"]))

    with pytest.raises(ValueError) as ve:
        DialectHelper.get_dialect_logic(select_query, DataSchema, "fail")

    assert ve.match("Unsupported dialect: fail")
