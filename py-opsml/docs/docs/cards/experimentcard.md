
`Experimentcards` are used to store metrics and artifacts related to `DataCards` and `ModelCards`. While a experimentcard can be used as a object itself, it's best to use it as a context manager.

### Creating an Experiment
Experiments are unique context-managed executions that record all created cards and their associated metrics, params, and artifacts to a single card called a `Experimentcard`.

If you're familiar with how other libraries do it, then nothing is really going to seem new.

### Traditional Example

```python
from opsml import start_experiment, SklearnModel, ModelCard # (1)
from opsml.helpers.data import create_fake_data

with start_experiment(space="opsml", log_hardware=True) as exp: # (2)

    X, y = create_fake_data(n_samples=1200)
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X.to_numpy(), y.to_numpy().ravel())

    random_forest_classifier = SklearnModel(
        model=reg,
        sample_data=X_train,
        task_type=TaskType.Classification,
        preprocessor=StandardScaler(),
    )

    modelcard = ModelCard(
            interface=random_forest_classifier,
            tags=["foo:bar", "baz:qux"],
        )
    
    exp.register_card(modelcard) # (3)
    exp.log_metric("accuracy", 0.95) # (4)
    exp.log_parameter("epochs", 10) # (5)
```

### GenAI Example

```python
from opsml import start_experiment, PromptCard, Prompt

with start_experiment(space="opsml", log_hardware=True) as exp:

    prompt = Prompt(
        model="gpt-4o",
        prompt="what is 2 + 2?",
        provider="openai",
        system_prompt="You are a helpful assistant.",
    )

    # ... your code here to test and validate the prompt
    # exp.log_metric(...)
    # exp.log_parameter(...)
    # exp.log_artifact(...)

    prompt_card = PromptCard(prompt)
    exp.register_card(prompt_card)
```

You can now log into the opsml server and see your recent experiment and associated metadata


### Accessing the ExperimentCard

You can access the experiment card and it's associated metrics, parameters and artifacts by loading the card from the registry

```python

from opsml import CardRegistry, RegistryType

registry = CardRegistry(RegistryType.Experiment)

card = registry.load_card(uid="{{experiment uid}}")
```