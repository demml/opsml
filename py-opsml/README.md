<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

# OpsML: End-to-End AI Lifecycle Management

[![OpsML Unit Tests](https://github.com/demml/opsml/actions/workflows/lints-test.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lints-test.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

**[Documentation](https://demml.github.io/opsml/)** · **[Task Backlog](https://github.com/orgs/demml/projects/1)**

---

OpsML is an AI lifecycle management platform built for the governance of both traditional ML and agentic AI systems. Its central abstraction is the **card** — a versioned, encrypted, registry-tracked record that wraps data, models, experiments, prompts, agents, or services. Cards are created in Python or YAML, persisted to a Rust server, and visualized in a SvelteKit UI.

Teams use OpsML to bring structure and governance to AI systems: consistent versioning, artifact lineage, monitoring, and observability — from initial training through production deployment.

## What OpsML Covers

- **Traditional ML** — version and track datasets, models, and experiments with full artifact lineage
- **GenAI** — manage and version prompts across providers (OpenAI, Anthropic, etc.) with `PromptCard`
- **Agents** — register, version, and govern agents with `AgentCard`; define specs in YAML and manage the full lifecycle via CLI
- **Services** — bundle cards (models + prompts + agents) into versioned `ServiceCard` deployments with a YAML spec + CLI lock/install workflow
- **Monitoring** — drift detection and data profiling via [Scouter](https://github.com/demml/scouter)
- **Observability** *(beta)* — OpenTelemetry trace ingestion and span visualization for any instrumented service, not just agents
- **Evaluations** *(beta)* — offline and online GenAI evaluation tied to versioned prompt cards

## Quick Start

```bash
pip install opsml
```

Run a local demo (creates a SQLite database, starts the server + UI):

```bash
opsml ui start
opsml demo
```

### Traditional ML

```python
from opsml import SklearnModel, CardRegistry, TaskType, ModelCard
from sklearn import ensemble

X, y = ...  # your data

classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(X, y)

model_interface = SklearnModel(model=classifier, sample_data=X[:10], task_type=TaskType.Classification)
model_interface.create_drift_profile(alias="drift", data=X)

card = ModelCard(interface=model_interface, space="my-team", name="classifier")
CardRegistry("model").register_card(card)

print(card.version)  # e.g., "1.0.0"
```

### GenAI — Prompts

```python
from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

card = PromptCard(
    space="my-team",
    name="summary-prompt",
    prompt=Prompt(
        model="gpt-4o",
        provider="openai",
        messages="Summarize the following in one sentence: ${text}",
        system_instructions="Be concise.",
    ),
)

client = OpenAI()
user_message = card.prompt.bind(text="OpsML manages AI artifacts...").messages[0]

response = client.chat.completions.create(
    model=card.prompt.model,
    messages=[card.prompt.system_instructions[0].model_dump(), user_message.model_dump()],
)

CardRegistry("prompt").register_card(card)
```

### Agents

Agents are most commonly defined via an `opsmlspec.yaml` file and managed through the CLI. The YAML spec describes the agent's capabilities, skills, interfaces, and linked cards (prompts, models). The CLI resolves versions and installs artifacts.

```yaml
# opsmlspec.yaml
name: support-agent
space: platform-team
type: Agent

metadata:
  description: "Customer support agent for billing and account queries."
  tags: ["support", "billing"]

service:
  version: "1.0.0"
  write_dir: opsml_service
  cards:
    - alias: support-prompt
      space: platform-team
      name: support-prompt
      version: "1.*"
      type: prompt

  agent:
    name: support-agent
    description: "Customer support agent for billing and account queries."
    version: "1.0.0"
    capabilities:
      streaming: true
    supported_interfaces:
      - url: "https://agents.example.com/support/v1"
        protocol_binding: "HTTP+JSON"
    default_input_modes: ["text"]
    default_output_modes: ["text"]
    skills:
      - id: billing-query
        name: "Billing Query"
        description: "Handles billing questions and invoice lookups."
        tags: ["billing", "finance"]
        examples: ["What is my current balance?"]
        input_modes: ["text"]
        output_modes: ["text"]
```

```bash
opsml lock            # resolves card versions, creates opsml.lock
opsml install service # downloads artifacts to ./opsml_service
```

Registered agents are visible in the OpsML UI, which provides a playground for live testing, an evaluations dashboard, and an observability view for trace data.

## Architecture

OpsML is a polyglot system:

- **Rust** — all logic: server, client, SQL/storage backends, auth, encryption, versioning, and CLI (`crates/`)
- **Python** — top-level stubs only, exposed via PyO3/maturin. No client or server logic lives in Python.
- **SvelteKit** — UI compiled and embedded in the server binary

The Python package is a stub layer over the Rust core. Card creation, registry operations, storage, encryption, and the HTTP client are all implemented in Rust and called through PyO3 bindings. This means the full logic is testable in Rust without the Python layer, and the Python API gets the same correctness guarantees as the server.

Supported backends:

| Layer | Options |
|---|---|
| Database | SQLite, PostgreSQL, MySQL |
| Storage | Local, S3, GCS, Azure Blob |

## Feature Comparison

| Feature | OpsML | Others |
|---|:---:|:---:|
| Artifact-first approach (cards) | ✅ | ❌ |
| SemVer for all artifacts | ✅ | ❌ (rare) |
| Multi-cloud storage | ✅ | ✅ |
| Multi-database support | ✅ | ✅ |
| Authentication | ✅ | ✅ |
| Artifact encryption at rest | ✅ | ❌ (rare) |
| Artifact lineage | ✅ | ❌ (uncommon) |
| Data profiling | ✅ | ❌ |
| Real-time model monitoring | ✅ | ❌ (rare) |
| Observability (OpenTelemetry traces) *(beta)* | ✅ | ❌ (rare) |
| GenAI evaluation system *(beta)* | ✅ | ❌ (rare) |
| Agent registry + governance | ✅ | ❌ |
| Agent UI (playground, evaluations, observability) | ✅ | ❌ |
| Isolated environments | ✅ | ❌ |
| Single Python dependency | ✅ | ❌ |
| Open source | ✅ | ❌ (some) |

## Status

Some features are still in active development or beta. Test them and share feedback via [GitHub Issues](https://github.com/demml/opsml/issues).

| Feature | Status |
|---|---|
| Agent registry | Beta — functional, seeking feedback |
| Evaluation system | Beta — functional, seeking feedback |
| Observability system | Beta — functional, seeking feedback |
| Agent playground | Coming soon — not fully functional |
| Admin dashboard + RBAC policy management | Coming soon |

## Contributing

See the [contributing guide](./CONTRIBUTING.md). Outstanding items are tracked in the [project backlog](https://github.com/orgs/demml/projects/1).

Thanks to these [projects and people](./ATTRIBUTIONS.md) for the foundation we built on.
