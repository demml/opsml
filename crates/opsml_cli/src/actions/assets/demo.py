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
from opsml.experiment import Experiment
import numpy as np
from opsml.scouter.alert import AlertThreshold
from opsml.data import DataType
from opsml.helpers.data import create_fake_data
from opsml.model import TaskType
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn import ensemble  # type: ignore
from opsml.data import ColType, ColumnSplit, DataSplit
import matplotlib.pyplot as plt  # type: ignore
from sklearn.metrics import confusion_matrix  # type: ignore
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay
from sklearn.metrics import make_scorer, precision_score, recall_score

RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Info))
X, y = create_fake_data(n_samples=2000)

pos_label, neg_label = "bad", "good"


# taken from sklearn docs (https://scikit-learn.org/stable/auto_examples/model_selection/plot_cost_sensitive_learning.html#sphx-glr-auto-examples-model-selection-plot-cost-sensitive-learning-py)
def fpr_score(y, y_pred, neg_label, pos_label):
    cm = confusion_matrix(y, y_pred, labels=[neg_label, pos_label])
    tn, fp, _, _ = cm.ravel()
    tnr = tn / (tn + fp)
    return 1 - tnr


def plot_confusion_matrix(
    model: ensemble.RandomForestClassifier,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> plt.Figure:
    """
    Plot residuals for PyTorch model predictions.

    Args:
        y_test: True values as tensor or numpy array
        y_pred: Predicted values as tensor or numpy array
        style: Matplotlib style to use
        plot_size: Figure size as (width, height)

    Returns:
        matplotlib Figure object
    """

    tpr_score = recall_score  # TPR and recall are the same metric
    scoring = {
        "precision": make_scorer(precision_score, pos_label=pos_label),
        "recall": make_scorer(recall_score, pos_label=pos_label),
        "fpr": make_scorer(fpr_score, neg_label=neg_label, pos_label=pos_label),
        "tpr": make_scorer(tpr_score, pos_label=pos_label),
    }

    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

    PrecisionRecallDisplay.from_estimator(
        model, X_test, y_test, pos_label=pos_label, ax=axs[0], name="GBDT"
    )

    axs[0].plot(
        scoring["recall"](model, X_test, y_test),
        scoring["precision"](model, X_test, y_test),
        marker="o",
        markersize=10,
        color="tab:blue",
        label="Default cut-off point at a probability of 0.5",
    )
    axs[0].set_title("Precision-Recall curve")
    axs[0].legend()

    RocCurveDisplay.from_estimator(
        model,
        X_test,
        y_test,
        pos_label=pos_label,
        ax=axs[1],
        name="GBDT",
        plot_chance_level=True,
    )
    axs[1].plot(
        scoring["fpr"](model, X_test, y_test),
        scoring["tpr"](model, X_test, y_test),
        marker="o",
        markersize=10,
        color="tab:blue",
        label="Default cut-off point at a probability of 0.5",
    )
    axs[1].set_title("ROC curve")
    axs[1].legend()
    _ = fig.suptitle("Evaluation of the vanilla GBDT model")

    return fig


def random_forest_classifier(exp: Experiment):
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X.to_numpy(), y.to_numpy().ravel())

    fig = plot_confusion_matrix(reg, X, y)
    exp.log_figure(name="confusion_matrix.png", figure=fig)

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

    model.create_drift_profile(
        alias="custom_metric",
        data=[
            CustomMetric(
                name="custom",
                value=0.5,
                alert_threshold=AlertThreshold.Above,
            )
        ],
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


SPACE = "opsml_demo"
NAME = "opsml"

if __name__ == "__main__":
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

            classifier = random_forest_classifier(exp)

            modelcard = ModelCard(
                interface=classifier,
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
