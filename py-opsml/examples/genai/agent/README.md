# Agent examples

OpsML doesn't care which agent framework you use. These examples wire three different frameworks — OpenAI Agents SDK, Google ADK, and CrewAI — into the same OpsML evaluation and tracing pipeline. The agent code is yours; OpsML handles the prompts, eval scenarios, service registration, and observability.

## What's in here

```
agent/
├── opsmlspec.yaml              # service registration spec
├── opsml.lock                  # locked card versions (generated)
├── prompts/
│   └── support_agent.yaml      # standardized prompt card
├── shared/
│   ├── setup.py                # AppState bootstrap + teardown
│   └── scenarios.jsonl         # golden eval scenarios
├── openai/
│   ├── agent.py                # OpenAI Agents SDK implementation
│   └── evaluate.py             # offline eval runner
├── google/
│   ├── agent.py                # Google ADK implementation
│   └── evaluate.py             # offline eval runner
├── crewai/
│   ├── agent.py                # CrewAI implementation
│   └── evaluate.py             # offline eval runner
└── run.py                      # CLI runner (no server needed)
```

## Setup

From `py-opsml/`:

```bash
uv run opsml lock --path examples/genai/agent/opsmlspec.yaml
```

This resolves the prompt card defined in `opsmlspec.yaml` and writes `opsml.lock`. The lock file pins exact card versions so evaluations are reproducible across environments.

## Running agents

### As a CLI (no server)

```bash
uv run python -m examples.genai.agent.run --backend openai "Help me plan dinner"
uv run python -m examples.genai.agent.run --backend google "My API times out"
uv run python -m examples.genai.agent.run --backend crewai "Debug this flaky test"
```

### As an API

```bash
uvicorn examples.genai.agent.openai.agent:app --port 8888
uvicorn examples.genai.agent.google.agent:app --port 8888
uvicorn examples.genai.agent.crewai.agent:app --port 8888
```

Each agent exposes a single `POST /ask` endpoint that accepts `{"query": "..."}` and returns `{"response": "..."}`.

### Running evaluations

```bash
uv run python -m examples.genai.agent.openai.evaluate
uv run python -m examples.genai.agent.google.evaluate
uv run python -m examples.genai.agent.crewai.evaluate
```

Every backend falls back to deterministic local responses when no API key is set (`OPENAI_API_KEY` or `GOOGLE_API_KEY`), so you can run evaluations without credentials to validate the pipeline end-to-end.

## How it works

### The spec file

`opsmlspec.yaml` registers this agent as an OpsML service. It declares which prompt cards the agent depends on, the agent's A2A capabilities, and deployment metadata:

```yaml
service:
  cards:
    - alias: support_prompt
      path: "prompts/support_agent.yaml"
      registry_type: prompt
```

The `alias` is how your code references the card at runtime — `app.service["support_prompt"]` returns a `PromptCard` with the resolved prompt text, model config, and evaluation tasks attached.

### Prompt cards

`prompts/support_agent.yaml` is OpsML's standardized prompt format. A single file defines the prompt text, the target model, and evaluation criteria:

```yaml
prompt:
  model: gemini-3.1-flash
  provider: Google
  messages:
    - "You are a practical assistant. Ask clarifying questions when needed..."
evaluation:
  alias: interactive_support_agent
  tasks:
    - task_type: Assertion
      id: response_is_string
      context_path: response
      operator: IsString
      expected_value: true
    - task_type: TraceAssertion
      id: trace_latency_budget
      operator: LessThan
      expected_value: 7000.0
      assertion:
        TraceDuration: {}
```

Evaluation tasks live next to the prompt they test. When you change the prompt, the assertions travel with it — no separate config to keep in sync.

### Golden eval scenarios

`shared/scenarios.jsonl` contains the test cases. Each line is a scenario with an initial query, expected outcome, simulated user persona, and per-scenario assertion tasks:

```json
{
  "id": "plan_weeknight_dinner",
  "initial_query": "Help me plan a weeknight dinner with ingredients and steps.",
  "expected_outcome": "A practical dinner plan the user can execute.",
  "simulated_user_persona": "busy home cook",
  "termination_signal": "DONE",
  "max_turns": 4,
  "tasks": [{"task_type": "Assertion", "id": "final_response_is_string", ...}]
}
```

### Shared setup

`shared/setup.py` bootstraps the OpsML `AppState` from the spec file and configures tracing. Every agent backend imports `get_shared_config()` to get the resolved prompt and eval scenarios. The config is created once and cached:

```python
app = AppState.from_spec(
    path=_SPEC_DIR / "opsmlspec.yaml",
    transport_config=_transport_config(),
    register=False,
)
app.instrument(batch_config=BatchConfig(scheduled_delay_ms=200))
```

`register=False` means the agent loads its cards from the lock file without contacting the OpsML server. Set `APP_ENV=staging` or `APP_ENV=production` to switch to gRPC transport for live Scouter ingestion.

## Agent implementations

Each backend follows the same pattern: import the shared config, build the framework-specific agent using the prompt from the card, and wire in an eval callback. The differences are only in framework API surface.

### OpenAI Agents SDK (`openai/agent.py`)

```python
from agents import Agent, Runner

agent = Agent(
    name="openai_interactive_agent",
    instructions=config.prompt.prompt.message.text,  # from the prompt card
    model="gpt-4.1-mini",
)
result = Runner.run_sync(agent, query, hooks=EvalHooks(...))
```

`EvalHooks` fires on `on_agent_end` and pushes an `EvalRecord` into the Scouter trace queue.

### Google ADK (`google/agent.py`)

```python
from google.adk.agents import Agent

agent = Agent(
    model=config.prompt.prompt.model,
    instruction=config.prompt.prompt.message.text,
    after_model_callback=self._after_model_callback,
)
```

The `after_model_callback` captures the response and emits the eval record. Google ADK is async, so the agent service exposes `async def run(query)`.

### CrewAI (`crewai/agent.py`)

```python
from crewai import Agent, Crew, LLM, Task

qa_agent = Agent(
    role="Interactive Support Assistant",
    backstory=config.prompt.prompt.message.text,
    llm=LLM(model="gemini/gemini-2.5-flash", ...),
)
crew = Crew(agents=[qa_agent], tasks=[task], task_callback=on_task_complete)
crew.kickoff()
```

CrewAI also gets automatic OpenTelemetry instrumentation via `CrewAIInstrumentor`.

### Adding a new framework

The contract is minimal:

1. Accept a query string
2. Use the prompt from `config.prompt.prompt.message.text`
3. Return a response string
4. Emit an `EvalRecord` via `trace.get_tracer().start_as_current_span()` so evaluation and tracing work

That's it. The framework manages the agent loop however it wants.

## Scouter integration

Every agent call is wrapped in an OpenTelemetry-compatible span via Scouter's tracing API. This gives you two things:

**Tracing.** Each agent invocation produces spans that flow into Scouter's trace storage. You get latency breakdowns, call graphs, and the full request/response payload — viewable in the OpsML UI trace waterfall or any OTel-compatible backend.

**Evaluation.** The `EvalRecord` pushed into the span's queue links the agent's input/output to the evaluation profile defined in the prompt card. The `EvalOrchestrator` in each `evaluate.py` drives multi-turn conversations using a `simulated_user_fn`, collects the records, and runs assertion tasks against them:

```python
results = EvalOrchestrator(
    queue=config.app.queue,
    scenarios=config.scenarios,
    agent_fn=run_agent,
    simulated_user_fn=simulated_user_turn,
).run()
```

The orchestrator handles both **offline evaluation** (batch run against golden scenarios) and **online evaluation** (assertions checked against live traffic traces). Prompt-level tasks like `TraceDuration < 7000ms` run against the spans automatically.

## Environment variables

| Variable | Required by | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI backend | Agent API access. Falls back to local responses if unset. |
| `GOOGLE_API_KEY` | Google / CrewAI backends | Agent API access. Falls back to local responses if unset. |
| `APP_ENV` | All (optional) | Set to `staging` or `production` for gRPC transport to Scouter. Defaults to mock transport. |
