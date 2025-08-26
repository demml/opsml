from opsml.helpers.data import create_fake_data
from opsml.experiment import start_experiment, Experiment
from opsml import SklearnModel, TaskType, ModelCard, ServiceCard, Card
from opsml.model import ModelSaveKwargs
from opsml.scouter import PsiDriftConfig
from lightgbm import LGBMClassifier
from sklearn import ensemble  # type: ignore
import pandas as pd


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


def create_lgb_classifier(
    exp: Experiment,
    X: pd.DataFrame,
    y: pd.DataFrame,
) -> ModelCard:
    # Create and train model
    classifier = LGBMClassifier(n_estimators=5)
    classifier.fit(X.to_numpy(), y.to_numpy().ravel())

    model_interface = SklearnModel(
        model=classifier,
        sample_data=X[0:10],
        task_type=TaskType.Classification,
    )

    model_interface.create_drift_profile(
        alias="lgb_psi",
        config=PsiDriftConfig(),
        data=X,
    )

    modelcard = ModelCard(
        interface=model_interface,
        space="opsml",
        name="lgb_model",
    )

    # register model
    exp.register_card(
        modelcard,
        save_kwargs=ModelSaveKwargs(
            save_onnx=True,
            onnx={
                "target_opset": {"ai.onnx.ml": 3, "": 9},
                "options": {
                    "zipmap": False,
                },
            },
        ),
    )

    return modelcard


with start_experiment(space="opsml") as exp:
    # create data
    X, y = create_fake_data(n_samples=1200)

    rf_model = create_random_forest_classifier(exp, X, y)
    lgb_model = create_lgb_classifier(exp, X, y)

    service_card = ServiceCard(
        space="opsml",
        name="classification_service",
        cards=[
            Card(alias="rf", card=rf_model),
            Card(alias="lgb", card=lgb_model),
        ],
    )
    exp.register_card(service_card)
