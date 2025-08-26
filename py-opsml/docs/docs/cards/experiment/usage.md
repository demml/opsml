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
But in cases where you want to provide a space and name, you can do so by specifying both arguments. In this case, any time the same space and names are re-used, a new version will be created.

| Argument         | Type                  | Default       | Description                                                   |
|------------------|-----------------------|---------------|---------------------------------------------------------------|
| `space`          | `str | None`         | `None`        | Space to associate with the `ExperimentCard`.                |
| `name`           | `str | None`         | `None`        | Name to associate with the `ExperimentCard`. Defaults to random name    |
| `code_dir`       | `Path | None`        | `None`        | Directory to log code from.                                   |
| `log_hardware`   | `bool`               | `False`       | Whether to log hardware information or not.                   |
| `experiment_uid` | `str | None`         | `None`        | Experiment UID. If provided, the experiment will be loaded from the server. |