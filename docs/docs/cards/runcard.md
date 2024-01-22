# RunCard

`RunCards` are use to store metrics and artifacts related to `DataCards` and `ModelCards`. While a RunCard can be used as a object itself, it's best when used as part of a `Project` run.

### Creating A Run
Runs are unique context-managed executions associated with a `Project` that record all created cards and their associated metrics, params, and artifacts to a single card called a `RunCard`.

The following example shows how to create a simple run as well as use `CardInfo` to store helper info

```python
from sklearn.linear_model import LinearRegression

from opsml import (
    CardInfo,
    DataCard,
    DataSplit,
    ModelCard,
    OpsmlProject,
    PandasData,
    ProjectInfo,
    SklearnModel,
)
from opsml.helpers.data import create_fake_data

info = ProjectInfo(name="opsml-project", repository="opsml", contact="user@email.com")

# create card info and set NAME, REPOSITORY, and CONTACT as environment variables
card_info = CardInfo(name="linear-reg", repository="opsml", contact="user@email.com").set_env()

# create project
project = OpsmlProject(info=info)

with project.run() as run:
    # create fake data
    X, y = create_fake_data(n_samples=1000, task_type="regression")
    X["target"] = y

    # Create data interface
    data_interface = PandasData(
        data=X,
        data_splits=[
            DataSplit(label="train", column_name="col_1", column_value=0.5, inequality=">="),
            DataSplit(label="test", column_name="col_1", column_value=0.5, inequality="<"),
        ],
        dependent_vars=["target"],
    )

    # Create datacard
    datacard = DataCard(interface=data_interface)
    run.register_card(card=datacard)

    # split data
    data = datacard.split_data()

    # fit model
    reg = LinearRegression()
    reg.fit(data.train.X.to_numpy(), data.train.y.to_numpy())

    # create model interface
    interface = SklearnModel(model=reg, sample_data=data.train.X.to_numpy())

    # create modelcard
    modelcard = ModelCard(interface=interface, to_onnx=True, datacard_uid=datacard.uid)

    # you can log metrics view log_metric or log_metrics
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})

    # log parameter
    run.log_parameter("test_parameter", 10)

    # register modelcard
    run.register_card(card=modelcard)

    # example of logging artifact to file
    with Path("artifact.txt").open("w") as f:
        f.write("This is a test")

    run.log_artifact_from_file("artifact", "artifact.txt")
```


You can now log into the `Opsml` server and see your recent run and associated metadata

::: opsml.RunCard
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

::: opsml.projects.OpsmlProject
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3

