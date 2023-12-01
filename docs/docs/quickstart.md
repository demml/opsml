To get a quick feel for `Opsml`, run the following code in a new terminal. The following uses Mlflow as a UI interface and local storage and sqlite.

### Start Local Server

<div class="termy">

```console
$ opsml-cli launch-uvicorn-app

...
<span style="color: green;">INFO</span>:     [INFO] Started server process
<span style="color: green;">INFO</span>:     [INFO] Waiting for application startup
<span style="color: green;">INFO</span>:     [INFO] Using worker: uvicorn.workers.

...
<span style="color: green;">INFO</span>:     [INFO] Application startup complete
<span style="color: green;">INFO</span>:     [INFO] Uvicorn running on http://0.0.0.0:8888
```

</div>

Next, open a new terminal and run the following python script. Make sure to set the `OPSML_TRACKING_URI` which tells `opsml` where to log experiments.


## Run Initial Python Script

```bash
export OPSML_TRACKING_URI=${YOUR_TRACKING_URI}
```

```python

import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

from opsml.projects import ProjectInfo
from opsml.projects.mlflow import MlflowProject
from opsml.registry import DataCard, ModelCard


def fake_data():
    X_train = np.random.normal(-4, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X = pd.DataFrame(X_train, columns=col_names)
    y = np.random.randint(1, 10, size=(1000, 1))
    return X, y


info = ProjectInfo(
    name="opsml",
    team="devops",
    user_email="test_email",
)

# start mlflow run
project = MlflowProject(info=info)
with project.run(run_name="test-run") as run:

    # create data and train model
    X, y = fake_data()
    reg = LinearRegression().fit(X.to_numpy(), y)

    # Create and registry DataCard with data profile
    data_card = DataCard(
        data=X,
        name="pipeline-data",
        team="mlops",
        user_email="mlops.com",
    )
    data_card.create_data_profile()
    run.register_card(card=data_card)

    # Create and register ModelCard with auto-converted onnx model
    model_card = ModelCard(
        trained_model=reg,
        sample_input_data=X[0:1],
        name="linear_reg",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        tags={"name": "model_tag"},
    )
    run.register_card(card=model_card)

    # log some metrics
    for i in range(0, 10):
        run.log_metric("mape", i, step=i)
```


## Opsml UI

### Models

List models by team

<p align="left">
  <img src="../images/list-models.png"  width="449" height="413"/>
</p>

List models by version

<p align="left">
  <img src="../images/model-screen.png" width="540" height="508"/>
</p>

### Data

Show data by version

<p align="left">
  <img src="../images/data-screen.png" width="612" height="508"/>
</p>


### Project UI

Project UI lists all projects and recent runs


TODO(@thorrester): opsml image
<p align="center">
  <img src="../images/opsml_ui.png"  width="1512" height="402" alt="opsml"/>
</p>

### Run UI

Within the run UI, you will see the various auto-recorded artifacts from your `Cards` and `Run`

TODO(@thorrester): opsml image
<p align="center">
  <img src="../images/opsml_run.png"  width="1841" height="792" alt="opsml run"/>
</p>
