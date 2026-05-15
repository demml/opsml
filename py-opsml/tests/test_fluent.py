from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import opsml
import opsml.sklearn
import pytest
from opsml import CardRegistries, start_experiment
from opsml.experiment import Metric, Parameter, get_experiment_metrics, get_experiment_parameters
from opsml.mock import OpsmlTestServer
from sklearn.linear_model import LogisticRegression  # type: ignore
from tests.conftest import WINDOWS_EXCLUDE


def _assert_no_active_experiment() -> None:
    with pytest.raises(RuntimeError, match="no active experiment"):
        opsml.active_experiment()


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_metric_no_active_raises():
    with pytest.raises(RuntimeError, match="no active experiment"):
        opsml.log_metric("accuracy", 0.9)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_exception_inside_with_pops_active():
    with OpsmlTestServer(cleanup=True):
        with pytest.raises(ValueError, match="boom"):
            with start_experiment(space="fluent", name="raises"):
                raise ValueError("boom")

        _assert_no_active_experiment()


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_two_sequential_experiments_isolate():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="one") as exp1:
            opsml.log_metric("metric_one", 1.0)

        with start_experiment(space="fluent", name="two") as exp2:
            opsml.log_metric("metric_two", 2.0)

        metric_names_1 = {metric.name for metric in get_experiment_metrics(exp1.card.uid)}
        metric_names_2 = {metric.name for metric in get_experiment_metrics(exp2.card.uid)}

        assert "metric_one" in metric_names_1
        assert "metric_two" not in metric_names_1
        assert "metric_two" in metric_names_2
        assert "metric_one" not in metric_names_2


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_active_stack_depth_zero_after_with():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="normal"):
            assert opsml.active_experiment() is not None

        _assert_no_active_experiment()


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_metric_uses_active():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="metric") as exp:
            opsml.log_metric("accuracy", 0.91)

        metrics = get_experiment_metrics(exp.card.uid)
        assert any(metric.name == "accuracy" and metric.value == 0.91 for metric in metrics)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_metrics_uses_active():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="metrics") as exp:
            opsml.log_metrics([Metric(name="loss", value=0.1), Metric(name="loss", value=0.2)])

        metrics = get_experiment_metrics(exp.card.uid)
        assert len(metrics) == 2


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_param_uses_active():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="param") as exp:
            opsml.log_param("n_estimators", 10)

        params = get_experiment_parameters(exp.card.uid)
        assert any(param.name == "n_estimators" for param in params)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_params_dict_form():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="params-dict") as exp:
            opsml.log_params({"alpha": 0.1, "solver": "lbfgs"})

        names = {param.name for param in get_experiment_parameters(exp.card.uid)}
        assert {"alpha", "solver"}.issubset(names)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_params_list_form():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="params-list") as exp:
            opsml.log_params([Parameter(name="alpha", value=0.1)])

        params = get_experiment_parameters(exp.card.uid)
        assert any(param.name == "alpha" for param in params)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_artifact_uses_active(tmp_path: Path):
    path = tmp_path / "artifact.txt"
    path.write_text("hello")

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="artifact") as exp:
            opsml.log_artifact(str(path))

        assert any(path.endswith("artifact.txt") for path in exp.card.list_artifacts())


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_artifacts_directory(tmp_path: Path):
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "one.txt").write_text("one")
    (artifact_dir / "two.txt").write_text("two")

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="artifacts") as exp:
            opsml.log_artifacts(str(artifact_dir))

        files = set(exp.card.list_artifacts())
        assert any(path.endswith("one.txt") for path in files)
        assert any(path.endswith("two.txt") for path in files)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_log_figure_matplotlib():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="figure") as exp:
            fig, ax = plt.subplots()
            ax.plot([1, 2], [3, 4])
            opsml.log_figure("line.png", fig)
            plt.close(fig)

        assert any(path.endswith("line.png") for path in exp.card.list_artifacts())


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_set_tag_persists_on_exit():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="tag") as exp:
            opsml.set_tag("source:mlflow-migration")

        loaded = CardRegistries().experiment.load_card(uid=exp.card.uid)
        assert "source:mlflow-migration" in loaded.tags


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_set_tags_replaces():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="tags") as exp:
            opsml.set_tags(["a", "b"])
            opsml.set_tags(["c"])

        loaded = CardRegistries().experiment.load_card(uid=exp.card.uid)
        assert loaded.tags == ["c"]


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_set_tag_then_set_tags_replaces():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="tags-replace") as exp:
            opsml.set_tag("a")
            opsml.set_tags(["b", "c"])

        loaded = CardRegistries().experiment.load_card(uid=exp.card.uid)
        assert loaded.tags == ["b", "c"]


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_nested_experiment_stack():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="outer") as outer:
            opsml.log_metric("outer_before", 1.0)
            with outer.start_experiment(space="fluent", name="inner") as inner:
                opsml.log_metric("inner_only", 2.0)
            opsml.log_metric("outer_after", 3.0)

        outer_names = {metric.name for metric in get_experiment_metrics(outer.card.uid)}
        inner_names = {metric.name for metric in get_experiment_metrics(inner.card.uid)}

        assert {"outer_before", "outer_after"}.issubset(outer_names)
        assert "inner_only" not in outer_names
        assert "inner_only" in inner_names


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_active_experiment_returns_current():
    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="fluent", name="active") as exp:
            assert opsml.active_experiment().card.uid == exp.card.uid


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_active_experiment_outside_raises():
    _assert_no_active_experiment()


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_full_mlflow_parity_smoke():
    X = np.random.rand(50, 4)
    y = (X.sum(axis=1) > 2).astype(int)
    clf = LogisticRegression().fit(X, y)

    with OpsmlTestServer(cleanup=True):
        with start_experiment(space="parity", name="rust-fluent") as exp:
            card = opsml.sklearn.log_model(clf, name="lr", sample_data=X[:5])
            opsml.log_metric("accuracy", 0.97)
            opsml.log_params({"penalty": "l2", "C": 1.0})
            opsml.set_tag("source:mlflow-migration")
            assert opsml.active_experiment().card.uid == exp.card.uid

        assert card.version is not None
