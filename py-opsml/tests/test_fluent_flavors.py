import numpy as np
import pytest
from opsml import CardRegistry, RegistryType, TaskType, start_experiment
from opsml.mock import OpsmlTestServer

from tests.conftest import WINDOWS_EXCLUDE


def _assert_registered(card):
    assert card.uid is not None
    assert card.version is not None
    loaded = CardRegistry(registry_type=RegistryType.Model).load_card(uid=card.uid)
    assert loaded.uid == card.uid
    assert loaded.version == card.version
    assert loaded.name == card.name
    return loaded


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_sklearn_log_model_round_trip():
    opsml_sklearn = pytest.importorskip("opsml.sklearn")
    linear_model = pytest.importorskip("sklearn.linear_model")

    X = np.random.rand(40, 4)
    y = (X.sum(axis=1) > 2).astype(int)
    model = linear_model.LogisticRegression().fit(X, y)

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="sklearn") as exp:
            card = opsml_sklearn.log_model(
                model,
                name="sklearn-lr",
                sample_data=X[:5],
                task_type=TaskType.Classification,
            )

        loaded_model = _assert_registered(card)
        loaded_exp = CardRegistry(registry_type=RegistryType.Experiment).load_card(uid=exp.card.uid)
        assert loaded_model.experimentcard_uid == exp.card.uid
        assert card.uid in loaded_exp.uids.modelcard_uids


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_sklearn_log_model_requires_active_experiment():
    opsml_sklearn = pytest.importorskip("opsml.sklearn")
    linear_model = pytest.importorskip("sklearn.linear_model")

    X = np.random.rand(40, 4)
    y = (X.sum(axis=1) > 2).astype(int)
    model = linear_model.LogisticRegression().fit(X, y)

    with OpsmlTestServer(cleanup=True):
        with pytest.raises(RuntimeError, match="no active experiment"):
            opsml_sklearn.log_model(
                model,
                name="sklearn-lr",
                space="flavors",
                sample_data=X[:5],
                task_type=TaskType.Classification,
            )


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_xgboost_log_model_round_trip():
    opsml_xgboost = pytest.importorskip("opsml.xgboost")
    xgb = pytest.importorskip("xgboost")

    X = np.random.rand(20, 4)
    y = (X.sum(axis=1) > 2).astype(int)
    dtrain = xgb.DMatrix(X, y)
    model = xgb.train(
        {"max_depth": 2, "eta": 1, "objective": "binary:logistic"},
        dtrain,
        num_boost_round=2,
    )

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="xgboost"):
            card = opsml_xgboost.log_model(
                model,
                name="xgb",
                sample_data=dtrain,
                task_type=TaskType.Classification,
            )

        _assert_registered(card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_lightgbm_log_model_round_trip():
    opsml_lightgbm = pytest.importorskip("opsml.lightgbm")
    lgb = pytest.importorskip("lightgbm")

    X = np.random.rand(20, 4)
    y = (X.sum(axis=1) > 2).astype(int)
    dataset = lgb.Dataset(X, y)
    model = lgb.train(
        {"objective": "binary", "verbosity": -1},
        dataset,
        num_boost_round=2,
    )

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="lightgbm"):
            card = opsml_lightgbm.log_model(
                model,
                name="lgb",
                sample_data=dataset,
                task_type=TaskType.Classification,
            )

        _assert_registered(card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_catboost_log_model_round_trip():
    opsml_catboost = pytest.importorskip("opsml.catboost")
    catboost = pytest.importorskip("catboost")

    X = np.random.rand(20, 4)
    y = (X.sum(axis=1) > 2).astype(int)
    model = catboost.CatBoostClassifier(iterations=2, verbose=False).fit(X, y)

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="catboost"):
            card = opsml_catboost.log_model(
                model,
                name="catboost",
                sample_data=X[:5],
                task_type=TaskType.Classification,
            )

        _assert_registered(card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_torch_log_model_round_trip():
    opsml_torch = pytest.importorskip("opsml.torch")
    torch = pytest.importorskip("torch")

    model = torch.nn.Linear(4, 1)
    sample = torch.rand(5, 4)

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="torch"):
            card = opsml_torch.log_model(
                model,
                name="torch-linear",
                sample_data=sample,
                task_type=TaskType.Regression,
            )

        _assert_registered(card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_lightning_log_model_with_trainer():
    opsml_lightning = pytest.importorskip("opsml.lightning")
    lightning = pytest.importorskip("lightning")
    torch = pytest.importorskip("torch")

    class LightningModule(lightning.LightningModule):
        def __init__(self):
            super().__init__()
            self.layer = torch.nn.Linear(1, 1)

        def forward(self, x):
            return self.layer(x)

        def training_step(self, batch, batch_idx):
            x, y = batch
            return torch.nn.functional.mse_loss(self(x), y)

        def configure_optimizers(self):
            return torch.optim.SGD(self.parameters(), lr=0.01)

    data = torch.utils.data.TensorDataset(torch.rand(8, 1), torch.rand(8, 1))
    trainer = lightning.Trainer(
        max_epochs=1,
        logger=False,
        enable_checkpointing=True,
        enable_model_summary=False,
    )
    trainer.fit(LightningModule(), torch.utils.data.DataLoader(data, batch_size=4))

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="lightning"):
            card = opsml_lightning.log_model(
                trainer,
                name="lightning-trainer",
                sample_data=torch.rand(2, 1),
                task_type=TaskType.Regression,
            )

        _assert_registered(card)


@pytest.mark.tensorflow
@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_tensorflow_log_model_round_trip():
    opsml_tensorflow = pytest.importorskip("opsml.tensorflow")
    tf = pytest.importorskip("tensorflow")

    model = tf.keras.Sequential([tf.keras.layers.Input(shape=(4,)), tf.keras.layers.Dense(1)])
    sample = np.random.rand(5, 4)

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="tensorflow"):
            card = opsml_tensorflow.log_model(
                model,
                name="tf",
                sample_data=sample,
                task_type=TaskType.Regression,
            )

        _assert_registered(card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_huggingface_log_model_with_tokenizer_and_hf_task():
    opsml_huggingface = pytest.importorskip("opsml.huggingface")
    transformers = pytest.importorskip("transformers")
    from opsml import HuggingFaceTask

    config = transformers.BertConfig(
        vocab_size=32,
        hidden_size=8,
        num_hidden_layers=1,
        num_attention_heads=1,
        intermediate_size=16,
    )
    model = transformers.BertModel(config)

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="huggingface"):
            card = opsml_huggingface.log_model(
                model,
                name="hf",
                hf_task=HuggingFaceTask.FeatureExtraction,
                task_type=TaskType.Nlp,
            )

        _assert_registered(card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_onnx_log_model_round_trip():
    opsml_onnx = pytest.importorskip("opsml.onnx")
    onnx = pytest.importorskip("onnx")
    helper = onnx.helper
    tensor_proto = onnx.TensorProto

    input_tensor = helper.make_tensor_value_info("input", tensor_proto.FLOAT, [None, 4])
    output_tensor = helper.make_tensor_value_info("output", tensor_proto.FLOAT, [None, 4])
    node = helper.make_node("Identity", inputs=["input"], outputs=["output"])
    graph = helper.make_graph([node], "identity", [input_tensor], [output_tensor])
    model = helper.make_model(
        graph,
        ir_version=11,
        opset_imports=[helper.make_operatorsetid("", 11)],
    )

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="flavors", name="onnx"):
            card = opsml_onnx.log_model(
                model,
                name="onnx-identity",
                sample_data=np.random.rand(5, 4).astype("float32"),
                task_type=TaskType.Regression,
            )

        _assert_registered(card)
