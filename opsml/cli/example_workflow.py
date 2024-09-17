from multiprocessing import Process
from opsml.cli.launch_server import launch_uvicorn_app
import time


def launch_app_in_background(port: int = 8888) -> Process:
    """
    Launches a Uvicorn Opsml server in the background

    Args:
        port:
            Default port to use with the opsml server
    """

    p = Process(target=launch_uvicorn_app, args=(port,))
    p.start()
    time.sleep(10)

    return p


def cli() -> None:
    # start the server app
    p = launch_app_in_background()

    # start the client app
    import os

    os.environ["OPSML_TRACKING_URI"] = "http://localhost:8888"

    from typing import cast
    import numpy as np
    import pandas as pd
    from scouter import DriftConfig
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler

    from opsml import (
        CardInfo,
        DataCard,
        DataSplit,
        ModelCard,
        PandasData,
        SklearnModel,
    )
    from opsml.helpers.data import create_fake_data
    from opsml.projects import ActiveRun, OpsmlProject, ProjectInfo

    class Pipeline:
        def __init__(self) -> None:
            self.info = CardInfo(repository="opsml", contact="user")
            self.project = OpsmlProject(
                info=ProjectInfo(
                    name="example-project",
                    repository=self.info.repository,
                    contact=self.info.contact,
                )
            )

        def create_datacard(self, run: ActiveRun) -> DataCard:
            X, y = create_fake_data(n_samples=20_000, n_features=20, n_categorical_features=4, task_type="regression")
            X["target"] = y

            interface = PandasData(
                data=X,
                data_splits=[
                    DataSplit(
                        label="train",
                        column_name="col_1",
                        column_value=0.2,
                        inequality=">=",
                    ),
                    DataSplit(
                        label="test",
                        column_name="col_1",
                        column_value=0.2,
                        inequality="<",
                    ),
                ],
                dependent_vars=["target"],
            )

            datacard = DataCard(
                interface=interface,
                name="example-datacard",
                repository=self.info.repository,
                contact=self.info.contact,
            )
            run.register_card(datacard)

            return datacard

        def create_modelcard(self, run: ActiveRun, datacard: DataCard) -> None:
            split_data = datacard.interface.split_data()

            assert split_data is not None, "No split data detected in datacard"

            X = cast(pd.DataFrame, split_data["train"].X)
            y = cast(pd.DataFrame, split_data["train"].y)

            reg = LinearRegression().fit(X.to_numpy(), y.to_numpy())

            interface = SklearnModel(
                model=reg,
                sample_data=X.to_numpy().astype(np.float32)[0:1],
                preprocessor=StandardScaler(),
            )

            X["target"] = y
            interface.create_drift_profile(
                data=X,
                drift_config=DriftConfig(targets=["target"]),
            )

            modelcard = ModelCard(
                interface=interface,
                name="example-modelcard",
                repository=self.info.repository,
                contact=self.info.contact,
            )

            run.register_card(card=modelcard)

        def start_run(self) -> None:
            with self.project.run(log_hardware=True) as run:
                datacard = self.create_datacard(run)
                self.create_modelcard(run, datacard)

    Pipeline().start_run()
    p.terminate()
