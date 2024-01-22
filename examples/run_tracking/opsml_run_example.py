from pathlib import Path

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
card_info = CardInfo(name="linear-reg", repository="opsml", contact="user@email.com")

# create project
project = OpsmlProject(info=info)


def run_project():
    # create run
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
        datacard = DataCard(interface=data_interface, info=card_info)
        run.register_card(card=datacard)

        # split data
        data = datacard.split_data()

        # fit model
        reg = LinearRegression()
        reg.fit(data.train.X.to_numpy(), data.train.y.to_numpy())

        # create model interface
        interface = SklearnModel(model=reg, sample_data=data.train.X.to_numpy())

        # create modelcard
        modelcard = ModelCard(interface=interface, info=card_info, to_onnx=True, datacard_uid=datacard.uid)

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


if __name__ == "__main__":
    run_project()

    # cleanup
    Path("artifact.txt").unlink()
