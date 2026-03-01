# YAML-Based Card Definitions

OpsML supports defining agents and prompts **entirely in YAML** — no Python required at definition time. Combined with `opsml lock` and `opsml install`, this lets you treat your AI service configuration the same way you treat infrastructure-as-code: version-controlled, diffable, and reproducible.

This is particularly useful for:

- **CI/CD pipelines** where you want to lock and install services without running Python.
- **Multi-team workflows** where prompt engineers own YAML files that developers consume.
- **Iterative agent development** where you want the registry to automatically skip re-registration when nothing has changed.

---

## Content Hashing: No Unnecessary Version Bumps

Both `PromptCard` and `AgentCard`/`ServiceCard` implement **content hashing**. When you run `opsml lock`, each card's content is SHA-256 hashed (excluding runtime-generated fields like `uid`, `created_at`, and `version`) and compared against the registry.

- **If the hash matches an existing card** → the lock reuses that card's version and UID. No new version is created.
- **If the hash is new** → the card is registered and gets a new version.

This means `opsml lock` is safe to run on every commit. It only increments versions when content actually changes.

```
First lock:   my-prompt → registered as 0.1.0
Second lock:  my-prompt → same content hash → reuses 0.1.0 (no new version)
Edit prompt:  my-prompt → new content hash  → registered as 0.2.0
```

---

## Project Layout

A YAML-based agent service typically looks like this:

```
my-agent/
├── opsml_spec.yaml          # top-level service definition
├── agent/
│   ├── agent_spec.yaml      # AgentSpec (can be inline or a separate file)
│   └── skills/
│       └── data-analysis/
│           └── SKILL.md     # Skill body loaded from filesystem
└── prompts/
    └── my_prompt.yaml       # PromptCard definition
```

---

## Defining Prompts in YAML

Prompt cards can be defined as standalone YAML files and referenced from the service spec by path.

```yaml
# prompts/my_prompt.yaml
space: platform-team
name: support-prompt
prompt:
  model: gpt-4o
  provider: openai
  messages:
    - "Analyze the sentiment of the provided text: {input}"
  system_instructions:
    - "You are a concise, professional support assistant."
  settings:
    temperature: 0.3
    max_tokens: 512
```

### With Evaluation Tasks

Prompt YAML files can also include an `evaluation` section to define assertion tasks that run against agent outputs. These evaluations are linked to the prompt and surfaced in the Evaluations dashboard.

```yaml
# prompts/my_prompt.yaml
space: platform-team
name: support-prompt
prompt:
  model: gpt-4o
  provider: openai
  messages:
    - "Analyze the sentiment of the provided text: {input}"
  system_instructions:
    - "You are a helpful assistant."

evaluation:
  alias: sentiment_analysis_eval
  tasks:
    - task_type: Assertion
      id: sentiment_score_check
      context_path: sentiment.score
      operator: GreaterThan
      expected_value: 18
      description: Sentiment score is above threshold
      depends_on: []

    - task_type: Assertion
      id: validate_email
      context_path: user.email
      operator: IsEmail
      expected_value: true
      description: Validate email format
      depends_on: []
```

---

## Defining an Agent in YAML

### Option 1: Inline Agent Spec

The `agent` spec can be written directly inside `opsml_spec.yaml` under `service.agent`:

```yaml
# opsml_spec.yaml
name: support-agent
space: platform-team
type: Agent

metadata:
  description: "Customer support agent."
  language: python
  tags: ["support"]

service:
  cards:
    - alias: my_prompt
      path: "prompts/my_prompt.yaml"  # (1)
      type: prompt

  agent:
    name: "Support Agent"
    description: "An agent that handles support queries."
    version: "1.0.0"
    provider:
      organization: "Acme Corp"
      url: "https://acme.example.com"
    capabilities:
      streaming: true
      push_notifications: false
      extended_agent_card: false
      extensions: []
    default_input_modes: ["text"]
    default_output_modes: ["text"]
    skills:
      - format: a2a
        id: billing-query
        name: "Billing Query"
        description: "Handles billing questions and invoice lookups."
        tags: ["billing", "finance"]
        examples:
          - "What is my current balance?"
          - "Show me my last invoice."
        input_modes: ["text"]
        output_modes: ["text"]
    security_schemes:
      api_key:
        name: "X-API-Key"
        location: "header"
    security_requirements:
      - schemes: ["api_key"]

deploy:
  - environment: production
    urls: ["https://agents.example.com/support/v1"]
```

1. Prompt cards can be referenced by `path` to a local YAML file rather than by registry `uid`. The CLI resolves and registers them during `opsml lock`.

### Option 2: External Agent Spec File

For larger agents or when you want to keep the spec separately versioned, point `service.agent` at a path:

```yaml
# opsml_spec.yaml
name: support-agent
space: platform-team
type: Agent

metadata:
  description: "Customer support agent."

service:
  agent: "agent/agent_spec.yaml"  # (1)

deploy:
  - environment: production
    urls: ["https://agents.example.com/support/v1"]
```

1. When `agent` is a string path, the CLI loads the `AgentSpec` from that file. This allows the agent spec to live independently of the top-level service config.

The referenced `agent/agent_spec.yaml` contains only the `AgentSpec` fields (no top-level `name`, `space`, or `type`):

```yaml
# agent/agent_spec.yaml
name: "Support Agent"
description: "An agent that handles support queries."
version: "1.0.0"
provider:
  organization: "Acme Corp"
  url: "https://acme.example.com"
capabilities:
  streaming: true
  push_notifications: false
  extended_agent_card: false
default_input_modes: ["text"]
default_output_modes: ["text"]
skills:
  - format: a2a
    id: billing-query
    name: "Billing Query"
    description: "Handles billing questions and invoice lookups."
    tags: ["billing"]
    examples:
      - "What is my current balance?"
  - format: standard
    name: "data-analysis"
    description: "Analyze data sets and generate reports."
    skills_path: "agent/skills/data-analysis"  # (1)
    license: "MIT"
    allowed_tools: ["pandas", "numpy"]
interface:
  - uri: "https://agents.example.com/support/v1"
    protocol_binding: "HTTP+JSON"
    protocol_version: "0.3.0"
    tenant: "default"
```

1. Standard-format skills can load their description body from a `SKILL.md` file on disk, keeping rich skill documentation alongside your code.

---

## Skill Files

Standard-format skills (`format: standard`) support loading their content from a `SKILL.md` file. The file uses YAML frontmatter for metadata and Markdown for the body:

```markdown
---
name: data-analysis
description: Analyze data sets and generate statistical reports from structured data.
---

## What this skill does

Processes tabular data (CSV, JSON, Parquet) and produces summary statistics,
trend analysis, and visualizations.

## When to use

Use this skill when the user asks to analyze, summarize, or visualize data.
```

The `skills_path` field in the agent spec points to the directory containing `SKILL.md`. The CLI loads the file content at lock time and stores it as part of the skill definition in the registry.

---

## CLI Workflow

```bash
# 1. Lock — resolve versions, check content hashes, register new/changed cards
opsml lock

# 2. Install — download locked service and all cards to local directory
opsml install service

# 3. Run your application pointing at the downloaded service
```

### Providing a custom spec file path

```bash
opsml lock --spec path/to/opsml_spec.yaml
opsml install service --spec path/to/opsml_spec.yaml
```

???tip "Lock is idempotent"
    Running `opsml lock` multiple times without changing any YAML files is safe and fast. Content hashes ensure that unchanged prompts and agent specs are never re-registered. Only cards whose YAML content has actually changed will receive new versions.

---

## How Content Hashing Works

When `opsml lock` processes a card:

1. The YAML is parsed and the card is constructed in memory.
2. A SHA-256 hash is computed over the card's serialized content, **excluding** runtime fields (`uid`, `created_at`, `space`, `name`, `version`).
3. The CLI queries the registry's `/card/compare_hash` endpoint with the hash.
4. If a matching hash is found, the existing card's metadata is reused. If not, the card is registered and gets the next version.

For `PromptCard`, the hash covers both the prompt content and the evaluation profile (with runtime fields stripped). For `AgentCard`/`ServiceCard`, the hash covers the full service configuration.

This means the hash is purely a function of **what you wrote** — not when or where it was registered.

---

## Full Example: Two-File Layout

=== "opsml_spec.yaml"

    ```yaml
    name: support-agent
    space: platform-team
    type: Agent

    metadata:
      description: "Customer support agent for billing and account queries."
      language: python
      tags: ["support", "billing"]

    service:
      cards:
        - alias: support_prompt
          path: "prompts/support_prompt.yaml"
          type: prompt

      agent: "agent/agent_spec.yaml"

    deploy:
      - environment: production
        urls: ["https://agents.example.com/support/v1"]
    ```

=== "agent/agent_spec.yaml"

    ```yaml
    name: "Support Agent"
    description: "Handles customer support queries for billing and accounts."
    version: "1.0.0"
    provider:
      organization: "Acme Corp"
      url: "https://acme.example.com"
    capabilities:
      streaming: true
      push_notifications: false
      extended_agent_card: false
    default_input_modes: ["text"]
    default_output_modes: ["text"]
    skills:
      - format: a2a
        id: billing-query
        name: "Billing Query"
        description: "Handles billing questions."
        tags: ["billing"]
        examples: ["What is my balance?"]
        input_modes: ["text"]
        output_modes: ["text"]
    interface:
      - uri: "https://agents.example.com/support/v1"
        protocol_binding: "HTTP+JSON"
        protocol_version: "0.3.0"
    security_schemes:
      api_key:
        name: "X-API-Key"
        location: "header"
    security_requirements:
      - schemes: ["api_key"]
    ```

=== "prompts/support_prompt.yaml"

    ```yaml
    space: platform-team
    name: support-prompt
    prompt:
      model: gpt-4o
      provider: openai
      messages:
        - "You are helping a customer with: {query}"
      system_instructions:
        - "Be concise and professional."
      settings:
        temperature: 0.2
        max_tokens: 256

    evaluation:
      alias: support_eval
      tasks:
        - task_type: Assertion
          id: response_quality
          context_path: response.quality_score
          operator: GreaterThan
          expected_value: 7
          description: Response quality score above threshold
          depends_on: []
    ```
