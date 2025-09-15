# Overview

`Opsml` is integrated with [Scouter](https://github.com/demml/scouter) for real-time monitoring. With this integration, you can the create drift profiles for your models and prompts, and monitor them in real-time. For a more detailed overview of Scouter, and how to use it, see the [Scouter documentation](https://docs.demml.io/scouter) along with our examples directory. The following is a brief overview of the Scouter integration with `Opsml`.


## Creating a Drift Profile

While you can create a drift profile for `ModelCards` and `PromptCards`, real-time monitoring requires that you setup the `Scouter` server. Refer to the setup instructions in the [Scouter documentation](https://docs.demml.io/scouter/docs/server/).

## ModelCards

When creating `ModelInterface` as part of a `ModelCard`, you can leverage the `create_drift_profile` method to create drift profile for your model. Refer to the **Scouter** documentation for supported types, but the process is the same for all types of model interfaces and cards.

### `create_drift_profile` Arguments

| Name | Required | Description |
| --- | --- | --- |
| **alias** | Yes | the alias for the drift profile. Interfaces can hold more than one drift profile. |
| **data** | Yes | The data to use for building the drift profile. Can be a pandas/polars dataframe, pyarrow table or numpy array |
| **config** | No | The drift config to use. Defaults to `SpcDriftConfig` |
| **data_type** | No | The type of data `DataType` to use. If None, data_type will be inferred from the data |


### Example

```python
from sklearn import ensemble

# Opsml Scouter imports
from opsml.scouter.alert import AlertThreshold, SlackDispatchConfig
from opsml.scouter.types import CommonCrons
from opsml.scouter.alert import PsiAlertConfig

# Opsml imports
from opsml.card import ModelCard, CardRegistry
from opsml.model import SklearnModel, TaskType
from opsml.data import DataType

reg = ensemble.RandomForestClassifier(n_estimators=5)
reg.fit(X.to_numpy(), y.to_numpy().ravel())

model = SklearnModel(
    model=reg,
    sample_data=X,
    task_type=TaskType.Classification,
)

# Create a PSI drift profile
model.create_drift_profile(
    alias="psi_data",
    data=X,
    config=PsiDriftConfig( # (1)
            alert_config=PsiAlertConfig(
                dispatch_config=SlackDispatchConfig(channel="#opsml"), # (2)
                features_to_monitor=["target"], # (3)
                schedule=CommonCrons.Every30Minutes,
            )
        ),
    data_type=DataType.Pandas,
)

# Create a custom drift profile
model.create_drift_profile(
        alias="custom_metric",
        data=[
            CustomMetric( # (4)
                name="custom",
                value=0.5,
                alert_threshold=AlertThreshold.Above,
            )
        ],
        config=CustomMetricDriftConfig(),
    )

# Create ModelCard
modelcard = ModelCard(
    interface=model,
    name="my_model",
    space="opsml",
    version="1.0.0",
)

registry = CardRegistry("model")
registry.register_card(modelcard)
```

1. The `PsiDriftConfig` is used to configure the PSI drift profile. You can also use other drift configs like `SpcDriftConfig`, `CustomMetricDriftConfig`, etc.
2. The `SlackDispatchConfig` is used to configure the alert dispatching to Slack. You can also use other dispatch configs.
3. The `features_to_monitor` is used to specify which features to monitor. If not specified, all features will be monitored. This is typically overkill.
4. The `CustomMetric` is used to create a custom drift profile.

## PromptCards

You can also create drift profiles for `PromptCards`. The only difference is that you will use the `create_drift_profile` method on the `PromptCard` instead of the `ModelInterface`, and you can only create LLM drift profiles and metrics.

For more information on LLM Monitoring, refer to [LLM Monitoring documentation](https://docs.demml.io/scouter/docs/monitoring/llm/overview/).

### `create_drift_profile` Arguments

| Name | Required | Description |
| --- | --- | --- |
| **alias** | Yes | The alias for the drift profile |
| **config** | Yes | The LLM drift config to use |
| **metrics** | Yes | The metrics to use for the drift profile. Must be a collection of `LMDriftMetric` objects |
| **workflow** | No | Optional custom workflow for advanced evaluation scenarios |


### Example (LLM as a Judge Drift Profile)

```python
from opsml.scouter.drift import LLMDriftConfig, LMDriftMetric, LLMDriftProfile
from opsml.scouter.alert import AlertThreshold
from opsml.llm import Score, Agent, Task, Workflow, Prompt


def create_reformulation_evaluation_prompt(): # (1)
    """
    Builds a prompt for evaluating the quality of a reformulated query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the reformulation.

    Example:
        >>> prompt = create_reformulation_evaluation_prompt()
    """
    return Prompt(
        message=(
            "You are an expert evaluator of search query reformulations. "
            "Given the original user query and its reformulated version, your task is to assess how well the reformulation improves the query. "
            "Consider the following criteria:"
            "- Does the reformulation make the query more explicit and comprehensive?"
            "- Are relevant synonyms, related concepts, or specific features added?"
            "- Is the original intent preserved without changing the meaning?"
            "- Is the reformulation clear and unambiguous?"
            "Provide your evaluation as a JSON object with the following attributes:"
            "- score: An integer from 1 (poor) to 5 (excellent) indicating the overall quality of the reformulation."
            "- reason: A brief explanation for your score."
            "Format your response as:"
            "{"
            '  "score": <integer 1-5>,'
            '  "reason": "<your explanation>"'
            "}"
            "Original Query:"
            "${user_query}"
            "Reformulated Query:"
            "${response}"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        response_format=Score,
    )

prompt = Prompt(
    model="gpt-4o",
    provider="openai",
    message="Hello, please reformulate the following query to make it more explicit and comprehensive: ${user_query}",
    system_instruction="You are a helpful assistant.",
)

card = PromptCard(prompt=prompt, space="opsml", name="opsml")

card.create_drift_profile(
    alias="llm_drift",
    config=LLMDriftConfig(),
    metrics=[
        LMDriftMetric(
            name="reformulation_quality",
            prompt=create_reformulation_evaluation_prompt(), # (2)
            value=3.0,
            alert_threshold=AlertThreshold.Below, # (3)
        )
    ],
)
```

1. The `create_reformulation_evaluation_prompt` function builds an evaluation prompt that we can use to assess the quality of query reformulations.
2. We feed the reformulation evaluation prompt to the `LMDriftMetric` to evaluate the quality of the reformulation.
3. The `alert_threshold` is set to `Below`, meaning that if the score is below the threshold, an alert will be triggered. Given the value of 3.0, this means that if the score is below 3.0, an alert will be triggered.

### Things to know

- There is no need to specify `space`, `name` or `version` with your drift config. These are automatically set based on the `ModelCard` or `PromptCard` you are using.


