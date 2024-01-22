# sklearn
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.metrics import mean_absolute_error

# Opsml
from opsml import CardInfo, DataCard, DataSplit, ModelCard, PandasData, SklearnModel
from opsml.helpers.data import create_fake_data
from opsml.helpers.logging import ArtifactLogger
from opsml.model.challenger import ModelChallenger
from opsml.projects import OpsmlProject, ProjectInfo

logger = ArtifactLogger.get_logger()


def create_champion():
    """This function is used to populate the data and model registry in order to test the ModelChallenger class"""
    """-------------------------------------DataCard-------------------------------------"""
    info = CardInfo(name="regression", repository="opsml", contact="user@example").set_env()
    info = ProjectInfo(name="opsml", repository="devops", contact="test_email")
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

        splits = datacard.split_data()

        reg = LinearRegression()
        reg.fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        run.log_metric("mae", value=mae)

        modelcard = ModelCard(
            interface=SklearnModel(model=reg, sample_data=splits.test.X.to_numpy()),
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
        )
        run.register_card(card=modelcard)


def create_challenger():
    """This function is used to populate the data and model registry in order to test the ModelChallenger class"""
    """-------------------------------------DataCard-------------------------------------"""
    info = CardInfo(name="regression", repository="opsml", contact="user@example").set_env()
    info = ProjectInfo(name="opsml", repository="devops", contact="test_email")
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

        splits = datacard.split_data()

        reg = Lasso()
        reg.fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        run.log_metric("mae", value=mae)

        modelcard = ModelCard(
            interface=SklearnModel(model=reg, sample_data=splits.test.X.to_numpy()),
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
        )

        challenger = ModelChallenger(challenger=modelcard)

        # this will compare the two models of the same name and return a report
        report = challenger.challenge_champion(
            metric_name="mae",
            metric_value=mae,  # could be metric from training
            lower_is_better=True,
        )

        if report["mae"][0].challenger_win:
            logger.info("Challenger won!")
            run.register_card(card=modelcard)
        else:
            logger.info("Challenger lost!")


if __name__ == "__main__":
    create_champion()
    create_challenger()
