import numpy as np
from opsml import (
    Card,
    CardDeck,
    DataCard,
    ModelCard,
    ModelCardMetadata,
    PandasData,
    Prompt,
    PromptCard,
    RegistryType,
    SklearnModel,
    start_experiment,
)
from opsml.core import LoggingConfig, LogLevel, RustyLogger
from opsml.data import ColType, ColumnSplit, DataSplit, DataType
from opsml.helpers.data import create_fake_data
from opsml.model import TaskType
from opsml.scouter.alert import AlertThreshold
from opsml.scouter.drift import CustomMetric, CustomMetricDriftConfig, PsiDriftConfig
from sklearn import ensemble  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore

RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Debug))
X, y = create_fake_data(n_samples=1200)


def random_forest_classifier():
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X.to_numpy(), y)

    model = SklearnModel(
        model=reg,
        sample_data=X,
        task_type=TaskType.Classification,
        preprocessor=StandardScaler(),
    )

    # create spc
    model.create_drift_profile(X)

    # create psi
    model.create_drift_profile(X, PsiDriftConfig(), DataType.Pandas)

    # custom
    metric = CustomMetric(name="custom", value=0.5, alert_threshold=AlertThreshold.Above)
    model.create_drift_profile([metric], CustomMetricDriftConfig())

    return model


def pandas_data() -> PandasData:
    split = DataSplit(
        label="train",
        column_split=ColumnSplit(
            column_name="col_1",
            column_value=0.4,
            column_type=ColType.Builtin,
            inequality="<=",
        ),
    )

    modified_data = X.copy()  # type: ignore
    # add a new column that is assigned a letter of the alphabet
    modified_data["col_2"] = np.random.choice(
        ["word1", "word2", "word3", "word4", "word5", "a", "b", "c"],
        size=len(modified_data),
    )

    interface = PandasData(
        data=modified_data,
        data_splits=[split],
        dependent_vars=["col_2"],
    )

    interface.create_data_profile(compute_correlations=True)

    return interface


def chat_prompt() -> Prompt:
    prompt = Prompt(
        model="gpt-4o",
        prompt="what is 2 + 2?",
        system_prompt="You are a helpful assistant.",
    )
    return prompt


def demo():
    """
    This is a demo function that runs an experiment and registers a model, prompt, and data card.
    """
    SPACE = "space2"
    NAME = "name"

    for i in range(0, 5):
        with start_experiment(space=SPACE, name=NAME, log_hardware=True) as exp:
            datacard = DataCard(
                interface=pandas_data(),
                space=f"{SPACE}_{i}",
                name=f"{NAME}_{i}",
                tags=["foo:bar", "baz:qux"],
            )
            exp.register_card(datacard)

            assert datacard.experimentcard_uid == exp.card.uid

            modelcard = ModelCard(
                interface=random_forest_classifier(),
                space=f"{SPACE}_{i}",
                name=f"{NAME}_{i}",
                to_onnx=True,
                tags=["foo:bar", "baz:qux"],
                metadata=ModelCardMetadata(
                    datacard_uid=datacard.uid,
                ),
            )
            exp.register_card(modelcard)

            assert modelcard.experimentcard_uid == exp.card.uid

            prompt_card = PromptCard(
                prompt=chat_prompt(),
                space=f"{SPACE}_{i}",
                name=f"{NAME}_{i}",
            )
            exp.register_card(prompt_card)

            initial_value = 100 + np.random.randint(0, 5)
            decay_rate = 0.05

            for i in range(0, 100):
                decay_value = initial_value * np.exp(-decay_rate * i)
                exp.log_metric(
                    name="step_metric",
                    value=decay_value,
                    step=i,
                )

            exp.log_metric(name="mae", value=np.random.rand())
            exp.log_parameter(name="param", value=np.random.rand())
            exp.log_parameter(name="param2", value=np.random.rand())
            exp.log_parameter(name="param3", value="this is my param")

            deck = CardDeck(
                space="test",
                name="test",
                cards=[
                    Card(
                        alias="model",
                        uid=modelcard.uid,
                        registry_type=RegistryType.Model,
                    ),
                    Card(
                        alias="data",
                        uid=datacard.uid,
                        registry_type=RegistryType.Data,
                    ),
                    Card(
                        alias="prompt",
                        uid=prompt_card.uid,
                        registry_type=RegistryType.Prompt,
                    ),
                ],
            )
            exp.register_card(deck)
