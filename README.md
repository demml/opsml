<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="300" height="300" alt="opsml logo"/>
  <br>
</h1>

### Quality Control for the Machine Learning Lifecycle

OpsML is an open-source developer-first ML operations platform focused on injecting quality control into the machine learning lifecycle. Leverage Opsml to **build**, **manage**, **track**, **monitor**, and **govern** your AI applications. Build with confidence, deploy with peace of mind.


[![CI](https://github.com/demml/opsml/actions/workflows/lints-test.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lints-test.yml)
[![Py-Versions](https://img.shields.io/badge/Python-3.9+-color=%2334D058)](https://pypi.org/project/opsml)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![llms.txt](https://img.shields.io/badge/llms.txt-green)](https://github.com/demml/opsml/blob/main/llm.txt)

<div align="center">
   <div>
      <a href="https://docs.demml.io/opsml/"><strong>Docs</strong></a> ·
      <a href="https://github.com/demml/opsml/issues/new/choose"><strong>Feature Request</strong></a>
   </div>
</div>
<br>

<div align="left">
  <b>Current status:</b> v3.0.0 pre-release (check release tags for latest 3.0.0-rc.* version)
</div>


## Table of Contents
- [Table of Contents](#table-of-contents)
- [Why OpsML?](#why-opsml)
  - [What makes OpsML different](#what-makes-opsml-different)
- [Installation](#installation)
- [Demo](#demo)
- [Example Usage (Traditional ML)](#example-usage-traditional-ml)
- [Example Usage (LLM)](#example-usage-llm)
- [Hosting](#hosting)
- [Us vs Others](#us-vs-others)
- [Contributing](#contributing)

## Why OpsML?

Building reliable ML systems shouldn't require gluing together dozens of disparate tools, each with their own quirks, gaps, and maintenance overhead. The modern ML stack is fragmented. While opsml can't solve every problem, it aims to provide a **unified foundation** for your machine learning lifecycle.

### What makes OpsML different

- **All-in-One Simplicity** – Models, data, prompts, experiments, services, and monitoring in one unified platform  
- **Type-Safe & Fast** – Rust-powered backend catches errors before production, not during and provides reliability and speed
- **Zero-Friction Integration** – Drop into existing workflows in minutes, no migration required  
- **Cloud & Database Agnostic** – Deploy anywhere, from local dev to multi-cloud production  
- **Production-Ready Controls** – Authentication, encryption, audit trails, and governance built-in  
- **Integrated Monitoring** – Real-time drift detection via [Scouter](https://github.com/demml/scouter) 
- **Standardized Patterns** – Consistent workflows across teams, projects, and environments  
- **Developer Happiness** – One dependency, unified API, maximum productivity  


## Installation

```bash
pip install "opsml==3.0.0rc15"
```

## Demo
Install the following dependencies to run the demo (if you don't have them already):

```bash
pip install scikit-learn
```

Then run the demo:

```bash
opsml demo
```

Now start the ui and navigate to `localhost:3000` in your browser (use `guest` as username and password):

```bash
opsml ui start
```

shutdown the ui when you're done:

```bash
opsml ui stop
```

## Example Usage (Traditional ML)

```python
# create_fake_data requires polars and pandas to be installed 
from opsml.helpers.data import create_fake_data
from opsml import SklearnModel, CardRegistry, TaskType, ModelCard, RegistryType
from sklearn import ensemble

# get model registry
reg = CardRegistry(RegistryType.Model)

# create data
X, y = create_fake_data(n_samples=1200)

# Create and train model
classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(X.to_numpy(), y.to_numpy().ravel())

model_interface = SklearnModel( 
    model=classifier,
    sample_data=X[0:10],
    task_type=TaskType.Classification,
)
model_interface.create_drift_profile(alias="drift", X)

modelcard = ModelCard(
    interface=model_interface,
    space="opsml",
    name="my_model",
)

# register model
reg.register_card(modelcard)
```

## Example Usage (LLM)

```python
from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt( 
        model="gpt-4o",
        provider="openai",
        message="Provide a brief summary of the programming language ${language}.", 
        system_instruction="Be concise, reply with one sentence.",
    ),
)

def chat_app(language: str):

    # create the prompt and bind the context
    user_prompt = card.prompt.bind(language=language).message[0].unwrap()
    system_instruction = card.prompt.system_instruction[0].unwrap()

    response = client.chat.completions.create(
        model=card.prompt.model_identifier,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)
```

## Hosting
OpsML can be hosted on any cloud provider or on-premises. It supports multi-cloud deployments and is compatible with various databases. You can run OpsML in isolated environments to avoid conflicts between staging and production. Check out the [hosting guide](https://docs.demml.io/opsml/docs/setup/overview/#server-mode) for more details.

## Us vs Others

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

## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](./CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started.

Thanks goes to these phenomenal [projects and people](./ATTRIBUTIONS.md) for creating a great foundation to build from!


