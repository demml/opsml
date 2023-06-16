# RunCard

`RunCards` are use to store metrics and artifacts related to `DataCards`, `ModelCards` and `PipelineCards`. While a RunCard can be used as a object itself, it's best when used as part of a `Project` run.

### Creating A Run
Runs are unique context-managed executions associated with a `Project` that record all created cards and their associated metrics, params, and artifacts to a single card called a `RunCard`.

The following example shows how to create a simple run as well as use `CardInfo` to store helper info

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_percentage_error

from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry import CardInfo, DataCard, ModelCard

card_info = CardInfo(name="linear-reg", team="opsml", user_email="user@email.com")

# to use runs, you must create and use a project
project_info = ProjectInfo(name="opsml-dev", team="opsml", user_email="user@email.com")
project = OpsmlProject(info=project_info)


def create_fake_data():
    X_train = np.random.normal(-4, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X = pd.DataFrame(X_train, columns=col_names)
    y = np.random.randint(1, 10, size=(1000, 1))

    return X, y


# start the run
with project.run(run_name="optional_run_name") as run:

    X, y = create_fake_data()

    # train model
    lasso = Lasso(alpha=0.5)
    lasso = lasso.fit(X.to_numpy(), y)

    preds = lasso.predict(X.to_numpy())

    mape = mean_absolute_percentage_error(y, preds)

    # Create metrics / params
    run.log_metric(key="mape", value=mape)
    run.log_parameter(key="alpha", value=0.5)

    data_card = DataCard(data=X, info=card_info)
    run.register_card(card=data_card, version_type="major")  # you can specify "major", "minor", "patch"

    model_card = ModelCard(
        trained_model=lasso,
        sample_input_data=X,
        datacard_uid=data_card.uid,
        info=card_info,
    )
    run.register_card(card=model_card)

print(run.runcard.get_metric("mape"))
# > Metric(name='mape', value=0.8489706297619047, step=None, timestamp=None)

print(run.runcard.get_parameter("alpha"))
# > Param(name='alpha', value=0.5)

```

### Creating A Run with MlFlow
If an `Opsml` server has been setup to use `Mlflow`, you can also associate an `MlflowProject` with a `RunCard`. The process is the same as above

```python

from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

from opsml.projects import ProjectInfo

from opsml.projects.mlflow import MlflowProject

from opsml.registry.cards import CardInfo
from opsml.registry import DataCard, ModelCard, CardRegistry


def fake_data():
    X_train = np.random.normal(-4, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X = pd.DataFrame(X_train, columns=col_names)
    y = np.random.randint(1, 10, size=(1000, 1))
    return X, y


info = ProjectInfo(name="opsml", team="devops", user_email="test_email",)
project = MlflowProject(info=info)
with project.run(run_name="mlflow-test") as run:

    X, y = fake_data()
    reg = LinearRegression().fit(X.to_numpy(), y)
    
    data_card = DataCard(
        data=X,
        name="pipeline-data",
        team="mlops",
        user_email="mlops.com",
    )
    run.register_card(card=data_card)

    model_card = ModelCard(
        trained_model=reg,
        sample_input_data=X[0:1],
        name="linear_reg",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
    )
    run.register_card(card=model_card)
    for i in range(0, 10):
        run.log_metric("test", i)
```

You can now log into the `Opsml` server and see your recent run and associated metadata

::: opsml.registry.RunCard
    options:
        members:
            - add_tag
            - add_tags
            - log_parameter
            - log_parameters
            - log_metric
            - log_metrics
            - log_artifact
        show_root_heading: true
        show_source: true
        heading_level: 3

::: opsml.projects.mlflow.project.MlflowProject
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3

