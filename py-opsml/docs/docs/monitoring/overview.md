# Overview

`Opsml` is integrated with [Scouter](https://github.com/demml/scouter) for real-time monitoring and observability. With this integration, you can the create drift profiles for your models and prompts and agents, and monitor them in real-time. For a more detailed overview of Scouter, and how to use it, see the [Scouter documentation](https://docs.demml.io/scouter) along with our examples directory. The following is a brief overview of the Scouter integration with `Opsml`.

## Creating a Drift Profile

While you can create a drift profile for `ModelCards`, `PromptCards` and `AgentCards`, real-time monitoring requires that you setup the `Scouter` server. Refer to the setup instructions in the [Scouter documentation](https://docs.demml.io/scouter/docs/server/).

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
from opsml.types import DataType

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
                baseline_value=0.5,
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

**Note on nomenclature**: In the context of `PromptCards`, drift profiles are often referred to as evaluation profiles, since they are typically used to evaluate the performance of prompts over time.

You can also create evaluation profiles for `PromptCards`. The only difference is that you will use the `create_eval_profile` method on the `PromptCard` instead of the `ModelInterface`. You can also provide a `GenAIEvalProfile` directly when creating the `PromptCard`.

For more information on GenAI Evaluations, refer to [LLM Monitoring documentation](https://docs.demml.io/scouter/docs/monitoring/genai/overview/).

### `create_eval_profile` Arguments
| Name | Required | Description |
| --- | --- | --- |
| **alias** | Yes | The alias for the evaluation profile |
| **config** | Yes | The GenAI drift config to use |
| **tasks** | Yes | The tasks to use for the evaluation profile. Must be a combination of `LLMJudgeTask` and `AssertionTask`. See [docs](https://docs.demml.io/scouter/docs/monitoring/genai/tasks/) |


### Example (LLM as a Judge Evaluation Profile)

```python
from opsml.scouter.evaluate import (
    GenAIAlertConfig,
    GenAIEvalConfig,
    GenAIEvalProfile,
    LLMJudgeTask,
)
from opsml.scouter.alert import AlertThreshold
from opsml.genai import Score, Agent, Task, Workflow, Prompt


def create_reformulation_evaluation_prompt():
    """
    Builds a prompt for evaluating the quality of a reformulated query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the reformulation.

    Example:
        >>> prompt = create_reformulation_evaluation_prompt()
    """
    return Prompt(
        messages=(
            "You are an expert evaluator of search query reformulations. "
            "Given the original user query and its reformulated version, your task is to assess how well the reformulation improves the query. "
            "Consider the following criteria:\n"
            "- Does the reformulation make the query more explicit and comprehensive?\n"
            "- Are relevant synonyms, related concepts, or specific features added?\n"
            "- Is the original intent preserved without changing the meaning?\n"
            "- Is the reformulation clear and unambiguous?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (poor) to 5 (excellent) indicating the overall quality of the reformulation.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "Original Query:\n"
            "${user_input}\n\n"
            "Reformulated Query:\n"
            "${reformulated_query}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        output_type=Score,
    )


def create_relevance_evaluation_prompt() -> Prompt:
    """
    Builds a prompt for evaluating the relevance of an LLM response to the original user query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the response's relevance.

    Example:
        >>> prompt = create_relevance_evaluation_prompt()
    """
    return Prompt(
        messages=(
            "You are an expert evaluator of LLM responses. "
            "Given the original user query and the LLM's response, your task is to assess how relevant the response is to the query. "
            "Consider the following criteria:\n"
            "- Does the response directly address the user's question or request?\n"
            "- Is the information provided accurate and appropriate for the query?\n"
            "- Are any parts of the response off-topic or unrelated?\n"
            "- Is the response complete and does it avoid unnecessary information?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (irrelevant) to 5 (highly relevant) indicating the overall relevance of the response.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "Original Query:\n"
            "${reformulated_query}\n\n"
            "LLM Response:\n"
            "${relevance_response}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        output_type=Score,
    )


relevance = LLMJudgeTask(
    id="relevance",
    prompt=create_relevance_evaluation_prompt(),
    expected_value=3.0,
    field_path="score",
    operator=ComparisonOperator.GreaterThanOrEqual,
    description="Evaluate the relevance of the LLM response to the user query",
)

reformulation = LLMJudgeTask(
    id="reformulation",
    prompt=create_reformulation_evaluation_prompt(),
    expected_value=3.0,
    field_path="score",
    operator=ComparisonOperator.GreaterThanOrEqual,
    description="Evaluate the quality of the query reformulation",
)

profile = GenAIEvalProfile(
    config=GenAIEvalConfig( # name, space, version are auto-set when registering the card
        sample_ratio=1,
        alert_config=GenAIAlertConfig(
            alert_condition=AlertCondition(
                baseline_value=0.80,
                alert_threshold=AlertThreshold.Below,
                delta=0.05,
            )
        ),
    ),
    tasks=[relevance, reformulation],
)

prompt = Prompt(
    model="gpt-4o",
    provider="openai",
    messages="Hello, please reformulate the following query to make it more explicit and comprehensive: ${user_query}",
    system_instructions="You are a helpful assistant.",
)

card = PromptCard(
    prompt=prompt,
    space="opsml",
    name="opsml",
    eval_profile={"genai_eval": profile} # (1)
)

### This is how you would create the evaluation profile on an existing PromptCard
card.create_drift_profile(
    alias="genai_eval",
    config=GenAIEvalConfig(
        sample_ratio=1,
        alert_config=GenAIAlertConfig(
            alert_condition=AlertCondition(
                baseline_value=0.80, # (2)
                alert_threshold=AlertThreshold.Below,  # (3)
                delta=0.05,
            )
        ),
    ),
    tasks=[relevance, reformulation],
)
```

1. The `eval_profile` argument is used to pass in the evaluation profile key and value when creating the `PromptCard`. (this is optional, you can also create the evaluation profile later using the `create_eval_profile` method).
2. The `baseline_value` is the value that the alert condition will be compared against.
3. The `alert_threshold` is used to specify whether the alert should be triggered when the value goes above or below the baseline value.

### Things to know

- There is no need to specify `space`, `name` or `version` with your evaluation config. These are automatically set based on the `ModelCard` or `PromptCard` you are using.


