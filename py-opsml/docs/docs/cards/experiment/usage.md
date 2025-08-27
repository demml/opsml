# Experiment Usage

For simplicity, the Opsml `ExperimentCard` and associated experiment functionality are designed to provide some parity with existing frameworks. This means that if you're familiar with how experiments are defined and used in other systems, you should find the Opsml approach to be quite similar.

**Note** - While OpsML is not designed to be an experiment tracking system like other model registry frameworks, its primary focus is managing the artifact lifecycle, which is critical for enterprise applications. However, since experiments are part of the artifact lifecycle and are artifacts themselves, OpsML includes experiment tracking capabilities. As experiment tracking tools vary widely, we are continually updating OpsML to improve parity. If you have specific needs, feel free to raise an issue or submit a pull request.


## Start an Experiment

To start an experiment with OpsML, you'll use the `start_experiment` context manager. Here's a basic example:

```python
from opsml import start_experiment

with start_experiment("opsml") as exp:
    # Define your experiment parameters and logic here
    pass
```

### Arguments

An `ExperimentCard` is created and versioned for every experiment run. You will often find that it's easiest to just provide the space to record to and let OpsML assign a random name to the experiment.
But in cases where you want to provide a space and name, you can do so by specifying both arguments. In this case, any time the same space and names are re-used, a new version will be created. **Note** - this is important for comparison purposes as experiments with the same space and name can be compared across versions.

| Argument         | Type                  | Default       | Description                                                   |
|------------------|-----------------------|---------------|---------------------------------------------------------------|
| `space`          | `str | None`         | `None`        | Space to associate with the `ExperimentCard`.                |
| `name`           | `str | None`         | `None`        | Name to associate with the `ExperimentCard`. Defaults to random name    |
| `code_dir`       | `Path | None`        | `None`        | Directory to log code from.                                   |
| `log_hardware`   | `bool`               | `False`       | Whether to log hardware information or not.                   |
| `experiment_uid` | `str | None`         | `None`        | Experiment UID. If provided, the experiment will be loaded from the server. |


## Parameters & metrics & figures, oh my!

Every experiment can log parameters, metrics, artifacts and figures. This is done using the `log_param`, `log_metric`, `log_figure` and `log_artifact` methods of the `Experiment` class.

- **Parameters** are inputs to your experiment that you want to track. This could include things like learning rate, batch size, or any other hyperparameters.
- **Metrics** are outputs from your experiment that you want to track. This could include things like accuracy, loss, or any other performance measure.
- **Figures** are visualizations that you want to track. This could include things like confusion matrices, ROC curves, or any other plots that help you understand your experiment.

```python
from opsml import start_experiment

with start_experiment("opsml") as exp:
    exp.log_param("learning_rate", 0.001)
    exp.log_metric("accuracy", 0.95)
    exp.log_figure("confusion_matrix.png", confusion_matrix)
    exp.log_artifact("my_local_artifact.txt")
```

### Artifacts

You can log artifacts from your local filesystem via the `log_artifact` or `log_artifacts` methods. **Note** - artifacts must already be saved to disk before they can be logged. More information can be found [here](../../api/experiment.md#opsml.experiment._experiment.Experiment.log_artifact)

- **log_artifact**: Intended for uploading a single artifact to the opsml server
- **log_artifacts**: Intended for uploading multiple artifacts to the opsml server. Must be a local directory

### Parameters

You can log parameters from your experiment via the `log_parameter` or `log_parameters` methods. **Note** - parameters must be simple data types (e.g. int, float, str) before they can be logged. More information can be found [here](../../api/experiment.md#opsml.experiment._experiment.Experiment.log_parameter)

- **log_parameter**: Intended for uploading a single parameter to the opsml server. Must be an integer, float or string.
- **log_parameters**: Intended for uploading multiple parameters to the opsml server. Can either be a list of `Parameter` objects or a dictionary of parameter names to values.


### Metrics

You can log metrics from your experiment via the `log_metric` or `log_metrics` methods. **Note** - metrics are expected to be floats. More information can be found [here](../../api/experiment.md#opsml.experiment._experiment.Experiment.log_metric)

- **log_metric**: Intended for uploading a single metric to the opsml server. Must be an integer, float or string.
- **log_metrics**: Intended for uploading a list of `Metric` to the opsml server.

### Figures

Opsml also allows you to associate figures to a given experiment through either the `log_figure_from_path` or `log_figure` methods. **Note** - To use `log_figure_from_path`, the figure must be saved to disk first. `log_figure` expects the figure object to be a `matplotlib.figure.Figure`. More information can be found [here](../../api/experiment.md#opsml.experiment._experiment.Experiment.log_figure)

- **log_figure_from_path**: Intended for uploading a figure from a file path to the opsml server.
- **log_figure**: Intended for uploading a figure object to the opsml server.
