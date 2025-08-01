from opsml import (
    SklearnModel,
    ModelCard,
    TaskType,
)
from opsml.helpers.data import create_fake_data
from sklearn import ensemble  # type: ignore


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
    return reg, X


def create_modelcard() -> ModelCard:
    """
    Creates a ModelCard for the trained model.
    """

    model, X = train_model()
    modelcard = ModelCard(
        interface=SklearnModel(
            model=model,
            sample_data=X,
            task_type=TaskType.Regression,
        ),
        space="opsml",
        name="eta",
    )
    return modelcard
