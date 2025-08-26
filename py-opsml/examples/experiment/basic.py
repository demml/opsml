import pandas as pd
from opsml import Card, DataCard, ModelCard, ServiceCard, SklearnModel, TaskType
from opsml.data import PandasData
from opsml.experiment import Experiment, start_experiment
from opsml.helpers.data import create_fake_data
from opsml.model import ModelSaveKwargs
from opsml.scouter import PsiDriftConfig
from sklearn import ensemble  # type: ignore


def create_random_forest_classifier(
    exp: Experiment,
    X: pd.DataFrame,
    y: pd.DataFrame,
) -> ModelCard:
    # Create and train model
    classifier = ensemble.RandomForestClassifier(n_estimators=5)
    classifier.fit(X.to_numpy(), y.to_numpy().ravel())

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

    return modelcard


def create_datacard(
    exp: Experiment,
    X: pd.DataFrame,
    y: pd.DataFrame,
):
    X["target"] = y

    data_interface = PandasData(X)

    datacard = DataCard(
        interface=data_interface,
        space="opsml",
        name="exp_basic",
    )

    # register data card
    exp.register_card(datacard)

    return datacard


with start_experiment(space="opsml", name="exp_basic") as exp:
    # create data
    X, y = create_fake_data(n_samples=1200)

    create_datacard(exp, X, y)
    rf_model = create_random_forest_classifier(exp, X, y)

    service_card = ServiceCard(
        space="opsml",
        name="exp_basic_service",
        cards=[Card(alias="rf", card=rf_model)],
    )
    exp.register_card(service_card)
