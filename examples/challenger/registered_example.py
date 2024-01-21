# sklearn
from sklearn.linear_model import Lasso, LinearRegression, QuantileRegressor
from sklearn.metrics import mean_absolute_error

# Opsml
from opsml import (
    CardInfo,
    CardRegistry,
    DataCard,
    DataSplit,
    ModelCard,
    PandasData,
    SklearnModel,
)
from opsml.helpers.data import create_fake_data
from opsml.helpers.logging import ArtifactLogger
from opsml.model.challenger import ModelChallenger
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.types import RegistryType

logger = ArtifactLogger.get_logger()


def populate_registry():
    """This function is used to populate the data and model registry in order to test the ModelChallenger class"""
    """-------------------------------------DataCard-------------------------------------"""
    info = CardInfo(name="challenger_example", repository="opsml", contact="user@example").set_env()
    data_reg = CardRegistry(RegistryType.DATA)

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
    data_reg.register_card(card=datacard)

    """-------------------------------------Create First Model-------------------------------------"""
    logger.info("starting linear regression model")
    info = ProjectInfo(name="opsml", repository="devops", contact="test_email")
    project = OpsmlProject(info=info)
    datacard = data_reg.load_card(RegistryType.DATA, info=CardInfo(uid=datacard.uid))
    splits = datacard.split_data()

    with project.run() as lin_run:
        reg = LinearRegression()
        reg.fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        lin_run.log_metric("mae", value=mae)

        model_card = ModelCard(
            interface=SklearnModel(model=reg, sample_data=splits.test.X.to_numpy()),
            name="linear_reg",
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
        )
        lin_run.register_card(card=model_card)

    """--------------------Create Second Model----------------------"""
    logger.info("starting lasso regression model")
    with project.run() as las_run:
        reg = Lasso()
        reg.fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        las_run.log_metric("mae", value=mae)

        model_card = ModelCard(
            interface=SklearnModel(model=reg, sample_data=splits.test.X.to_numpy()),
            name="lasso_reg",
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
        )
        las_run.register_card(card=model_card)

    """--------------------Create Third Model----------------------"""
    logger.info("starting quantile regression model")
    with project.run() as quant_run:
        reg = QuantileRegressor(solver="highs")
        reg.fit(splits.train.X.to_numpy(), splits.train.y)
        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        quant_run.log_metric("mae", value=mae)
        model_card = ModelCard(
            interface=SklearnModel(model=reg, sample_data=splits.test.X.to_numpy()),
            name="quantile_reg",
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
        )
        quant_run.register_card(card=model_card)


def compare_models():
    info = CardInfo(repository="opsml", contact="user@example").set_env()
    # lets first load the linear_reg model

    model_registry = CardRegistry("model")
    linreg_card = model_registry.load_card(
        name="linear_reg",
        repository=info.repository,
        tags={"example": "challenger"},
    )

    # Instantiate the challenger class and pass the linear_reg card as the challenger
    challenger = ModelChallenger(challenger=linreg_card)

    # Challenge 1 or more champion models based on the `mae` metric that was record for all models
    reports = challenger.challenge_champion(
        metric_name="mae",
        lower_is_better=True,
        champions=[
            CardInfo(name="lasso_reg", repository="opsml", version="1.0.0"),
            CardInfo(name="quantile_reg", repository="opsml", version="1.0.0"),
        ],
    )

    print([report.model_dump() for report in reports["mae"]])


if __name__ == "__main__":
    populate_registry()
    compare_models()
