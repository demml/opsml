from opsml import (
    start_experiment,
    PandasData,
    SklearnModel,
    Prompt,
    DataCard,
    ModelCard,
    ModelCardMetadata,
    PromptCard,
    ServiceCard,
    Card,
    RegistryType,
    ModelSaveKwargs,
    ModelSettings,
)
from opsml.logging import RustyLogger, LoggingConfig, LogLevel
from opsml.scouter.drift import (
    PsiDriftConfig,
    CustomMetric,
    CustomMetricDriftConfig,
)
import numpy as np
from opsml.scouter.alert import AlertThreshold
from opsml.types import DataType
from opsml.helpers.data import create_fake_data
from opsml.model import TaskType
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn import ensemble  # type: ignore
from opsml.data import ColType, ColumnSplit, DataSplit


RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Info))
X, y = create_fake_data(n_samples=2000)


def random_forest_classifier():
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X.to_numpy(), y.to_numpy().ravel())

    model = SklearnModel(
        model=reg,
        sample_data=X,
        task_type=TaskType.Classification,
        preprocessor=StandardScaler(),
    )

    # create spc
    model.create_drift_profile(alias="spc_data", data=X)

    # create psi
    model.create_drift_profile(
        alias="psi_data",
        data=X,
        config=PsiDriftConfig(),
        data_type=DataType.Pandas,
    )

    # custom
    metric = CustomMetric(
        name="custom",
        value=0.5,
        alert_threshold=AlertThreshold.Above,
    )
    model.create_drift_profile(
        alias="custom_metric",
        data=[metric],
        config=CustomMetricDriftConfig(),
    )

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
        message="what is 2 + 2?",
        system_instruction="You are a helpful assistant.",
        model_settings=ModelSettings(
            model="gpt-4o",
            provider="openai",
            temperature=0.7,
            top_p=1.0,
            max_tokens=100,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            parallel_tool_calls=False,
            stop_sequences=["\n"],
            seed=42,
            logit_bias={
                "123": 10,
                "456": 10,
            },
            extra_body={
                "custom": {
                    "key": "value",
                },
            },
        ),
    )
    return prompt


SPACE = "space"
NAME = "name"

for i in range(0, 10):
    with start_experiment(
        space=f"{SPACE}_{i}",
        name=f"{NAME}_{i}",
        log_hardware=True,
    ) as exp:
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
            tags=["foo:bar", "baz:qux"],
            metadata=ModelCardMetadata(
                datacard_uid=datacard.uid,
            ),
        )
        exp.register_card(modelcard, save_kwargs=ModelSaveKwargs(save_onnx=True))

        assert modelcard.experimentcard_uid == exp.card.uid

        prompt_card = PromptCard(
            prompt=chat_prompt(),
            space=f"{SPACE}_{i}",
            name=f"{NAME}_{i}",
            tags=["foo:bar", "baz:qux"],
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

        service = ServiceCard(
            space="service",
            name="service",
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
        exp.register_card(service)
