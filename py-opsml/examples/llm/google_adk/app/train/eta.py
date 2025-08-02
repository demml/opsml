from opsml import (
    SklearnModel,
    ModelCard,
    TaskType,
)
from opsml.helpers.data import create_fake_data
from sklearn import ensemble  # type: ignore
from opsml.scouter.drift import PsiDriftConfig
from opsml.scouter.alert import PsiAlertConfig
from opsml.scouter.types import CommonCrons
from opsml.data import DataType


def train_model() -> ensemble.RandomForestRegressor:
    """
    Trains a RandomForestRegressor model on fake data.
    """

    # create fake lat lon data
    X, y = create_fake_data(
        n_samples=20000,
        n_features=4,
        task_type="regression",
        n_categorical_features=0,
    )

    reg = ensemble.RandomForestRegressor(n_estimators=5)
    reg.fit(X.to_numpy(), y.to_numpy().ravel())
    return reg, X, y


def create_modelcard() -> ModelCard:
    """
    Creates a ModelCard for the trained model.
    """

    model, X, y = train_model()

    # append y to X for model interface
    X["target"] = y.to_numpy().ravel()

    interface = SklearnModel(
        model=model,
        sample_data=X,
        task_type=TaskType.Regression,
    )

    interface.create_drift_profile(
        alias="eta_metrics",
        data=X,
        config=PsiDriftConfig(
            alert_config=PsiAlertConfig(
                schedule=CommonCrons.Every6Hours,
            ),
        ),
        data_type=DataType.Pandas,
    )

    modelcard = ModelCard(interface=interface, space="opsml", name="eta")

    return modelcard
