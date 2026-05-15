# Fluent Experiment API

The fluent API is an MLflow-style layer over the existing `Experiment` methods.
It only works inside an active `with start_experiment(...)` block. OpsML does
not silently create an experiment when none is active.

```python
import opsml
from opsml import start_experiment

with start_experiment(space="examples", name="run"):
    opsml.log_metric("accuracy", 0.91)
    opsml.log_params({"n_estimators": 100, "criterion": "gini"})
    opsml.set_tag("source:mlflow-migration")
```

Available functions:

- `opsml.log_metric`
- `opsml.log_metrics`
- `opsml.log_param`
- `opsml.log_params`
- `opsml.log_artifact`
- `opsml.log_artifacts`
- `opsml.log_figure`
- `opsml.log_figure_from_path`
- `opsml.set_tag`
- `opsml.set_tags`
- `opsml.active_experiment`

The active experiment stack is process-global in this release. Concurrent
threads or asyncio tasks should use the explicit `exp.log_metric(...)` form on
a captured experiment object.

Framework model logging lives in typed flavor packages such as
`opsml.sklearn.log_model(...)`, `opsml.xgboost.log_model(...)`, and
`opsml.huggingface.log_model(...)`.
