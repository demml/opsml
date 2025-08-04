<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="300" height="400" alt="opsml logo"/>
  <br>
</h1>

<h3 align="center">Quality Control for the Machine Learning Artifacts</h3>
---

[![Unit Tests](https://github.com/demml/opsml/actions/workflows/lints-test.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lints-test.yml)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)


`OpsML` is a developer-first ML operations platform focused on injecting quality control into machine learning artifact management. `OpsML` provides a unified and ergonomic interface and experience for managing ML artifacts, enabling teams to collaborate more effectively and deploy with confidence, all while reducing engineering overhead and providing piece of mind.

## Highlights

- <span class="text-alert">**Consistency**</span>: OpsML provides a **foundation layer** for managing ML artifacts across the entire lifecycle.
- <span class="text-alert">**Built from Insanity**</span>: Built by those who've been there before and have experienced the pain of managing ML artifacts. We're also obsessed with quality control and providing a developer-first experience. 
- <span class="text-alert">**Performance**</span>: OpsML is built in Rust and is designed to be fast, reliable, and efficient, giving you peace of mind that your ML artifacts are in good hands.
- <span class="text-alert">**Integrations**</span>: OpsML is designed to be easy to integrate into your existing workflows and tech stack. In addition, we're continually adding intergrations to third-party libraries, providing developers with a hollistic and singular experience.
- <span class="text-alert">**No Auto Magic**</span>: OpsML is designed to be easy to use and understand, with no hidden magic or black boxes. Sure, we abstract things to make the experience consistent, but these abstractions are thin and transparent with accompanying documentation and code, so you know what's going on under the hood. 

### <span class="text-secondary">**Do any of the following apply to you?**</span>

- You don't currently have a consistent way to manage ML artifacts.
- You're using a variety of tools to manage ML artifacts across the entire lifecycle (why use many tool when few do trick?).
- You're tired of spending time on boilerplate code and want to focus on building models and applications.
- You want something that is easy to use and integrate into your existing workflows/tech stack.
- You are a developer, team, small company, large enterprise?
- You want a tool that has consistent support and maintenance and a team that is obsessed with quality control.
- You don't want to spend the brain power on figuring out how to manage all of your ML artifacts (you've got better things to do).

If you answered yes to any of the above, then `OpsML` is for you.

## See it in Action

### Traditional ML Workflow
``` py { title="ML Workflow Quickstart" }

# create_fake_data requires polars and pandas to be installed 
from opsml.helpers.data import create_fake_data
from opsml import SklearnModel, CardRegistry, TaskType,  ModelCard, RegistryType
from sklearn import ensemble  # type: ignore

# start registries
reg = CardRegistry(RegistryType.Model) # (1)

# create data
X, y = create_fake_data(n_samples=1200)

# Create and train model
classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(X.to_numpy(), y.to_numpy().ravel())

model_interface = SklearnModel(  # (2)
    model=classifier,
    sample_data=X[0:10],
    task_type=TaskType.Classification,
)
model_interface.create_drift_profile(alias="drift", X) # (3)

modelcard = ModelCard( # (4)
    interface=model_interface,
    space="opsml",
    name="my_model",
)

# register model
reg.register_card(modelcard)

# This code will run as is
```

1.  Create, read, update, and delete Cards via CardRegistries.
2.  The SklearnModel is one of several interfaces for storing models in OpsML.
3.  OpsML is integrated with our model monitoring library, [Scouter](https://github.com/demml/scouter), which allows you to create drift and data profiles and monitor your models in production.
4.  The ModelCard is the primary interface for storing models in OpsML. It is a wrapper around the model interface and provides additional functionality such as versioning, metadata, and artifact management.



???success "Example ModelCard Output"

    ``` json
    {
      "name": "my-model",
      "space": "opsml",
      "version": "0.3.0",
      "uid": "01962a48-e0cc-7961-9969-8b75eac4b0de",
      "tags": [
        "foo:bar",
        "baz:qux"
      ],
      "metadata": {
        "datacard_uid": "01962a48-e08c-7792-8a3a-6ecd6ad46d19",
        "experimentcard_uid": null,
        "auditcard_uid": null,
        "interface_metadata": {
          "task_type": "Classification",
          "model_type": "SklearnEstimator",
          "data_type": "Pandas",
          "onnx_session": null,
          "schema": {
            "items": {
              "col_8": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_1": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_3": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_2": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_4": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_5": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_6": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_9": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_7": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              },
              "col_0": {
                "feature_type": "float64",
                "shape": [
                  1
                ],
                "extra_args": {}
              }
            }
          },
          "save_metadata": {
            "model_uri": "model.joblib",
            "data_processor_map": {},
            "sample_data_uri": "data.parquet",
            "onnx_model_uri": "onnx-model.onnx",
            "drift_profile_uri": "drift"
          },
          "extra_metadata": {},
          "interface_type": "Sklearn",
          "model_specific_metadata": {
            "classes_": "[0 1]",
            "feature_importances_": "[0.10789112 0.09341817 0.09390145 0.10334441 0.08558507 0.10508047\n 0.09082737 0.10868374 0.10699015 0.10427807]",
            "n_classes_": 2,
            "n_features_in_": 10,
            "n_outputs_": 1,
            "params": {
              "bootstrap": true,
              "ccp_alpha": 0.0,
              "class_weight": null,
              "criterion": "gini",
              "max_depth": null,
              "max_features": "sqrt",
              "max_leaf_nodes": null,
              "max_samples": null,
              "min_impurity_decrease": 0.0,
              "min_samples_leaf": 1,
              "min_samples_split": 2,
              "min_weight_fraction_leaf": 0.0,
              "monotonic_cst": null,
              "n_estimators": 5,
              "n_jobs": null,
              "oob_score": false,
              "random_state": null,
              "verbose": 0,
              "warm_start": false
            }
          },
          "drift_type": [
            "Spc"
          ]
        }
      },
      "registry_type": "Model",
      "created_at": "2025-04-12T13:55:41.388075Z",
      "app_env": "development",
      "is_card": true,
      "opsml_version": "0.1.0"
    }
    ```

### GenAI
``` py { title="GenAI - OpenAI" }
from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="o4-mini",
        provider="openai",
        message="Provide a brief summary of the programming language $1.", # (1)
        system_instruction="Be concise, reply with one sentence.",
    ),
)

def chat_app(language: str):

    # create the prompt and bind the context
    user_prompt = card.prompt.message[0].bind(language).unwrap()

    response = client.chat.completions.create(
        model=card.prompt.model,
        messages=[
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": card.prompt.message[0].unwrap()},
        ],
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt") # (2)
    registry.register_card(card)

# This code will run as is
```

1.  OpsML prompts allow you to bind context and santize prompt messages.
2.  A CardRegistry can accept a **string** or a **RegistryType** (RegistryType.Prompt).

### Agentic Workflow via PydanticAI
``` py { title="Agent - PydanticAI" }
from pydantic_ai import Agent
from opsml import PromptCard, Prompt, CardRegistry, RegistryType

# Creating the card here for demonstration purposes
# In practice, you would create the card, register it and then load it from the registry
# whenever you need it for your application.
card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="gpt-4o",
        provider="openai",
        message='Where does "hello world" come from?',
        system_instruction="Be concise, reply with one sentence.",
    ),
)

agent = Agent(
    card.prompt.model_identifier,
    system_instruction=card.prompt.system_instruction[0].unwrap(),
)

result = agent.run_sync(card.prompt.message[0].unwrap())
print(result.output)

registry = CardRegistry(RegistryType.Prompt)
registry.register_card(card)

# This code will run as is
```

### <span class="text-secondary">**Us vs Others**</span>

| Feature | OpsML | Others |
|---------|:-------:|:--------:|
| **Artifact-First Approach** | ✅ | ❌ |
| **SemVer for All Artifacts** | ✅ | ❌ (rare) |
| **Multi-Cloud Compatibility** | ✅ | ✅ |
| **Multi-Database Support** | ✅ | ✅ |
| **Authentication** | ✅ | ✅ |
| **Encryption** | ✅ | ❌ (rare) |
| **Artifact Lineage** | ✅ | ❌ (uncommon) |
| **Out-of-the-Box Model Monitoring & Data Profiling** | ✅ | ❌ |
| **Isolated Environments (No Staging/Prod Conflicts)** | ✅ | ❌ |
| **Single Dependency** | ✅ | ❌ |
| **Low-friction Integration Into Your Current Tech Stack** | ✅ | ❌ |
| **Standardized Patterns and Workflows** | ✅ | ❌ |
| **Open Source** | ✅ | ❌ (some) |


