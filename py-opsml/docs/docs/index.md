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

## **What is it?**

`OpsML` is a developer-first ML operations platform focused on injecting quality control into machine learning artifact management. `OpsML` provides a unified and ergonomic interface and experience for managing ML artifacts, enabling teams to collaborate more effectively and deploy with confidence, all while reducing engineering overhead and providing piece of mind.

## Use case - Traditional ML Workflow
``` py { title="Quickstart" hl_lines="17-21 23-28"}
from opsml.helpers.data import create_fake_data
from typing import Tuple, cast
import pandas as pd
from opsml import SklearnModel, CardRegistry, TaskType,  ModelCard
from sklearn import ensemble  # type: ignore

# start registries
reg = CardRegistry(RegistryType.Model) # (1)

# create data
X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

# Create and train model
classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(X.to_numpy(), y.to_numpy().ravel())

model_interface = SklearnModel(  # (2)
    model=classifier,
    sample_data=X,
    task_type=TaskType.Classification,
)

modelcard = ModelCard( # (3)
    interface=model_interface,
    space="opsml",
    name="my_model",
    to_onnx=True,  # aut-convert to onnx (optional)
)

# register model
reg.model.register_card(modelcard)

# This code will run as is
```

1.  Create, read, update, and delete Cards via CardRegistries.
2.  The SklearnModel is one of several interfaces storing models in OpsML.
3.  The ModelCard is the primary interface for storing models in OpsML. It is a wrapper around the model interface and provides additional functionality such as versioning, metadata, and artifact management.

### Use Case - GenAI
``` py { title="GenAI" hl_lines="17-21 23-28"}
from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="gpt-4o",
        prompt="Provide a brief summary of the programming language $1.", # (1)
        system_prompt="Be concise, reply with one sentence.",
    ),
)

def chat_app(language: str):
    user_prompt = card.prompt.prompt[0].bind(language).unwrap()

    response = client.chat.completions.create(
        model=card.prompt.model,
        messages=[
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": card.prompt.prompt[0].unwrap()},
        ],
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)

# This code will run as is
```
1.  OpsML prompts allow you to bind context and santize prompt messages.

## Use Case - Agentic Workflow via PydanticAI
``` py { title="{Pydantic Agent}" }
from pydantic_ai import Agent
from opsml import PromptCard, Prompt, CardRegistry, RegistryType

# Creating the card here for demonstration purposes
# In practice, you would create the card, register it and then load it from the registry
# whenever you need it for your application.
card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="openai:gpt-4o",
        system_prompt="Be concise, reply with one sentence.",
    ),
)

agent = Agent(
    card.prompt.model,
    system_prompt=card.prompt.system_prompt[0].unwrap(),
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.data)

registry = CardRegistry(RegistryType.Prompt)
registry.register_card(card)

# This code will run as is
```

## **What is Quality Control?**

Quality control in the context of `OpsML` refers to:

### Developer-First Experience
- **Zero-friction Integration** - Drop into existing ML workflows in minutes
- **Type-safe and efficient by Design** - Rust in the back, python in the front<sup>*</sup>. Catch errors before they hit production
- **Unified API** - One consistent interface for all ML frameworks
- **Environment Parity** - Same experience from development to production
- **Dependency Overhead** - One dependency for all ML artifact management

### Built to Scale
- **Trading Cards for ML** - Manage ML artifacts like trading cards - collect, organize, share
- **Cloud-Ready** - Native support for AWS, GCP, Azure
- **Database Agnostic** - Support for SQLite, MySQL, Postgres
- **Modular Design** - Use what you need, leave what you don't

### Production Ready
- **High-Performance Server** - Built in Rust for speed, reliability and concurrency
- **Built-in Security** - Authentication and encryption out of the box
- **Audit-Ready** - Complete artifact lineage and versioning
- **Standardized Governance Workflows** - Consistent patterns to use across teams
- **Built-in Monitoring** - Integrated with Scouter

<sup>
*OpsML is written in Rust and is exposed via a Python API built with PyO3.
</sup>
