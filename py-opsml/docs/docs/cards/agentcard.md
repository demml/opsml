# AgentCard & Agent Registry

The **Agent Registry** is OpsML's purpose-built system for managing the full lifecycle of AI agents — from creation and versioning to governance, evaluation, and observability. Just like you register models and data, you register agents as first-class cards.

The goal of the Agent Registry is to **simplify and standardize agent creation, governance, and evaluation** across teams and environments. Whether you're deploying a customer-support assistant, a multi-skill research agent, or a complex multi-agent pipeline, the Agent Registry gives you a consistent, auditable, and interoperable way to manage it.

## Why an Agent Registry?

Agents present unique governance challenges compared to traditional ML models:

- **Interoperability** — agents need to discover and communicate with each other across systems.
- **Governance** — agent behavior, capabilities, and access controls must be versioned and auditable.
- **Evaluation** — prompt-linked evaluations need to be tracked alongside model performance.
- **Observability** — multi-turn, multi-skill agent interactions require structured trace visibility.

The Agent Registry addresses all of these through a combination of structured specifications, the A2A protocol standard, and a built-in UI for playground testing, evaluation dashboards, and trace waterfall views.

---

## A2A Protocol

Agent specifications in OpsML are based on the **[Agent-to-Agent (A2A) protocol](https://google.github.io/A2A/) v0.3.0** — an open standard for agent interoperability developed to enable consistent communication between agents regardless of framework or provider.

By grounding `AgentSpec` in A2A, OpsML ensures that:

- Agents registered in OpsML can be discovered and invoked by any A2A-compatible system.
- Agent capabilities, skills, and security schemes are described in a machine-readable, standard format.
- Multi-agent systems can be built compositionally without tight coupling between implementations.

---

## Quick Start

### Register an Agent

```python
from opsml import (
    AgentCard,
    AgentSpec,
    AgentCapabilities,
    AgentInterface,
    AgentSkill,
    SecurityRequirement,
    CardRegistry,
)

spec = AgentSpec(
    name="support-agent",
    description="Customer support agent for handling billing and account queries.",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
    ),
    supported_interfaces=[
        AgentInterface(
            url="https://agents.example.com/support/v1",
            protocol_binding="HTTP+JSON",
            protocol_version="0.3.0",
        )
    ],
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="billing-query",
            name="Billing Query",
            description="Handles billing questions and invoice lookups.",
            tags=["billing", "finance"],
            examples=["What is my current balance?", "Show me my last invoice."],
            input_modes=["text"],
            output_modes=["text"],
        ),
    ],
)

card = AgentCard(
    space="platform-team",
    name="support-agent",
    spec=spec,
)

registry = CardRegistry("agent")
registry.register_card(card)

print(card.version)  # e.g., "1.0.0"
```

### Load an Agent

```python
from opsml import CardRegistry

registry = CardRegistry("agent")

card = registry.load_card(space="platform-team", name="support-agent")
print(card.spec.capabilities.streaming)  # True
```

---

## Agent Specification

The `AgentSpec` is the core of every `AgentCard`. It is a structured, A2A-compliant description of what an agent can do, how to communicate with it, and what security requirements it has.

### Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | Yes | Human-readable name for the agent. |
| `description` | `string` | Yes | Description of the agent's purpose and capabilities. |
| `version` | `string` | Yes | Semantic version of the agent spec (e.g., `"1.0.0"`). |
| `capabilities` | `AgentCapabilities` | Yes | Feature flags the agent supports. |
| `supported_interfaces` | `list[AgentInterface]` | Yes | Communication interfaces the agent exposes. |
| `default_input_modes` | `list[string]` | Yes | Default input modalities (e.g., `["text", "image"]`). |
| `default_output_modes` | `list[string]` | Yes | Default output modalities (e.g., `["text", "json"]`). |
| `skills` | `list[AgentSkill]` | Yes | Specific capabilities the agent can perform. |
| `provider` | `AgentProvider` | No | Organization providing the agent. |
| `documentation_url` | `string` | No | Link to the agent's full documentation. |
| `icon_url` | `string` | No | URL to the agent's icon for UI display. |
| `security_schemes` | `dict[str, SecurityScheme]` | No | Named security scheme definitions. |
| `security_requirements` | `list[SecurityRequirement]` | No | Global security requirements for agent access. |
| `signatures` | `list[AgentCardSignature]` | No | JWS signatures verifying agent card authenticity. |

### AgentCapabilities

| Field | Type | Default | Description |
|---|---|---|---|
| `streaming` | `bool` | `False` | Whether the agent supports streaming responses. |
| `push_notifications` | `bool` | `False` | Whether the agent supports server-initiated push notifications. |
| `extended_agent_card` | `bool` | `False` | Whether the extended agent card format is supported. |
| `extensions` | `list[AgentExtension]` | `[]` | Custom capability extensions. |

### AgentInterface

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | `string` | Yes | Endpoint URL for the agent interface. |
| `protocol_binding` | `string` | Yes | Protocol binding (`"HTTP+JSON"`, `"JsonRpc"`, `"Grpc"`). |
| `protocol_version` | `string` | Yes | Protocol version (defaults to `"0.3.0"`). |
| `tenant` | `string` | No | Tenant identifier for multi-tenant deployments. |

### AgentSkill

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | Yes | Unique identifier for the skill. |
| `name` | `string` | Yes | Human-readable skill name. |
| `description` | `string` | Yes | What this skill does. |
| `tags` | `list[string]` | No | Categorization tags. |
| `examples` | `list[string]` | No | Example user prompts or inputs. |
| `input_modes` | `list[string]` | No | Supported input modalities. |
| `output_modes` | `list[string]` | No | Supported output modalities. |
| `security_requirements` | `list[SecurityRequirement]` | No | Per-skill security requirements. |

### AgentProvider

| Field | Type | Description |
|---|---|---|
| `organization` | `string` | Organization name. |
| `url` | `string` | Organization URL. |

---

## Security Schemes

Agents can declare the authentication methods they support through `security_schemes`. The following scheme types are available:

=== "API Key"

    ```python
    from opsml import ApiKeySecurityScheme, SecurityScheme

    scheme = SecurityScheme(
        ApiKeySecurityScheme(
            name="X-API-Key",
            location="header",
            description="API key for service authentication.",
        )
    )
    ```

=== "HTTP Bearer (JWT)"

    ```python
    from opsml import HttpAuthSecurityScheme, SecurityScheme

    scheme = SecurityScheme(
        HttpAuthSecurityScheme(
            scheme="Bearer",
            bearer_format="JWT",
        )
    )
    ```

=== "OAuth 2.0"

    ```python
    from opsml import (
        Oauth2SecurityScheme, OAuthFlows,
        AuthorizationCodeFlow, SecurityScheme,
    )

    scheme = SecurityScheme(
        Oauth2SecurityScheme(
            flows=OAuthFlows(
                authorization_code=AuthorizationCodeFlow(
                    authorization_url="https://auth.example.com/authorize",
                    token_url="https://auth.example.com/token",
                    pkce_required=True,
                    scopes={"read:agent": "Read agent data"},
                )
            )
        )
    )
    ```

=== "mTLS"

    ```python
    from opsml import MtlsSecurityScheme, SecurityScheme

    scheme = SecurityScheme(
        MtlsSecurityScheme(description="Mutual TLS required.")
    )
    ```

=== "OpenID Connect"

    ```python
    from opsml import OpenIdConnectSecurityScheme, SecurityScheme

    scheme = SecurityScheme(
        OpenIdConnectSecurityScheme(
            open_id_connect_url="https://auth.example.com/.well-known/openid-configuration"
        )
    )
    ```

To attach schemes to an `AgentSpec`:

```python
spec = AgentSpec(
    ...,
    security_schemes={"bearer": bearer_scheme, "apiKey": api_key_scheme},
    security_requirements=[SecurityRequirement(schemes=["bearer"])],
)
```

---

## Agent Registry Workflow

The Agent Registry follows the same versioned card lifecycle as the rest of OpsML:

```
Define AgentSpec → Create AgentCard → Register → Lock → Deploy
```

1. **Define** your `AgentSpec` with capabilities, interfaces, and skills.
2. **Create** an `AgentCard` wrapping the spec (optionally linking `PromptCards` for evaluation).
3. **Register** with `CardRegistry("agent")`.
4. **Lock** versions with `opsml lock` (when using `opsmlspec.yaml` with `type: Agent`).
5. **Deploy** and use the OpsML UI for playground testing, evaluations, and trace monitoring.

???tip "Define entirely in YAML"
    Agents and their linked prompts can be defined entirely in YAML without writing any Python. See [YAML-Based Card Definitions](yaml-definitions.md) for the full workflow including content hashing, skill files, and multi-file layouts.

---

## OpsML UI: Agent Features

Once an agent is registered, the OpsML UI provides three dedicated views for working with it.

### Playground

The **Playground** lets you interact with a live agent directly from the UI without writing any code.

- Select a skill from the agent's skill list.
- Send messages and receive responses in a chat interface.
- Toggle streaming mode for agents that support it.
- View raw request/response payloads in the debug sidebar.
- Multi-turn conversations are tracked using A2A `contextId` and `taskId` across turns.
- Configure authentication (API key, Bearer token, OAuth) inline without leaving the page.

This is useful for quick smoke tests, demo walkthroughs, and verifying agent behavior after a new version is deployed.

### Evaluations

The **Evaluations** dashboard connects your agent to linked `PromptCards` for structured performance tracking.

- Each `PromptCard` associated with the agent gets its own evaluation panel.
- Metrics are pulled from Scouter (when enabled) and displayed with time-range filtering.
- Records and workflow results are paginated per prompt card.
- Drift detection can be configured on the linked prompt cards to surface model degradation.

This view is the primary tool for **agent governance** — tracking whether agent behavior is stable across versions and over time.

### Observability (Traces)

The **Traces** view provides structured, waterfall-style visibility into agent execution.

- Every agent invocation is captured as a trace with hierarchical spans.
- The waterfall view shows timing, duration, and parent-child relationships between spans.
- Individual spans include events, attributes, and error details.
- Time-range filtering and infinite scroll make it easy to navigate high-volume trace data.

Traces are powered by Scouter's observability backend and follow OpenTelemetry conventions for span structure.

---

## Full AgentSpec YAML Reference

When using the `opsmlspec.yaml` workflow, the `agent` section configures the `AgentSpec` inline. See the [ServiceCard documentation](servicecard.md#agent-configuration) for details on the full spec file structure.

```yaml
name: support-agent
space: platform-team
type: Agent

metadata:
  description: "Customer support agent for billing and account queries."
  language: python
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
    provider:
      organization: "Acme Corp"
      url: "https://acme.example.com"

    supported_interfaces:
      - url: "https://agents.example.com/support/v1"
        protocol_binding: "HTTP+JSON"
        protocol_version: "0.3.0"
        tenant: "default"

    capabilities:
      streaming: true
      push_notifications: false
      extended_agent_card: false
      extensions: []

    default_input_modes: ["text"]
    default_output_modes: ["text"]

    skills:
      - id: billing-query
        name: "Billing Query"
        description: "Handles billing questions and invoice lookups."
        tags: ["billing", "finance"]
        examples:
          - "What is my current balance?"
          - "Show me my last invoice."
        input_modes: ["text"]
        output_modes: ["text"]

    security_schemes:
      bearer:
        http:
          scheme: Bearer
          bearer_format: JWT

    security_requirements:
      - schemes: ["bearer"]

    documentation_url: "https://docs.example.com/support-agent"
    icon_url: "https://example.com/icons/support-agent.png"
```

---

## AgentCard vs ServiceCard

`AgentCard` extends `ServiceCard` — everything you know about services applies to agents, with additional structure:

| Feature | ServiceCard | AgentCard |
|---|---|---|
| Card grouping | Yes | Yes |
| YAML spec (`opsmlspec.yaml`) | Yes | Yes (`type: Agent`) |
| CLI lock / install | Yes | Yes |
| A2A-compliant spec | No | Yes |
| Playground UI | No | Yes |
| Evaluation dashboard | Via prompt cards | Yes (built-in) |
| Trace waterfall | No | Yes |
| Skill definitions | No | Yes |
| Security scheme declarations | No | Yes |
