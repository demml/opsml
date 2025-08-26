import pandas as pd
from opsml import Card, ModelCard, ServiceCard, SklearnModel, TaskType
from opsml.experiment import Experiment, start_experiment
from opsml.helpers.data import create_fake_data
from opsml.model import ModelSaveKwargs
from opsml.scouter import PsiDriftConfig
from sklearn import ensemble  # type: ignore
from sklearn.metrics import log_loss  # type: ignore
from pydantic import BaseModel


class ModelParameters(BaseModel):
    n_estimators: int = 5
    criterion: str = "log_loss"
    min_samples_leaf: int = 2


def create_random_forest_classifier(
    exp: Experiment,
    X: pd.DataFrame,
    y: pd.DataFrame,
) -> ModelCard:
    # Create and train model
    parameters = ModelParameters()

    classifier = ensemble.RandomForestClassifier(
        n_estimators=parameters.n_estimators,
        criterion=parameters.criterion,
        min_samples_leaf=parameters.min_samples_leaf,
    )
    classifier.fit(X.to_numpy(), y.to_numpy().ravel())
    loss = log_loss(y.to_numpy(), classifier.predict_proba(X))

    model_interface = SklearnModel(
        model=classifier,
        sample_data=X[0:10],
        task_type=TaskType.Classification,
    )

    model_interface.create_drift_profile(
        alias="rf_psi",
        config=PsiDriftConfig(),
        data=X,
    )

    modelcard = ModelCard(
        interface=model_interface,
        space="opsml",
        name="rf_model",
    )

    # register model
    exp.register_card(
        card=modelcard,
        save_kwargs=ModelSaveKwargs(save_onnx=True),
    )

    # log parameters and metrics
    exp.log_parameters(parameters.model_dump())
    exp.log_metric("log_loss", loss)

    return modelcard


with start_experiment(space="opsml", name="exp_metrics") as exp:
    # create data
    X, y = create_fake_data(n_samples=1200)

    rf_model = create_random_forest_classifier(exp, X, y)

    service_card = ServiceCard(
        space="opsml",
        name="exp_basic_service",
        cards=[Card(alias="rf", card=rf_model)],
    )
    exp.register_card(service_card)
