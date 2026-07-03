# GenAI Metrics (Scouter) — OpsML Integration

This document describes the GenAI metrics feature added to OpsML: how the backend proxies Scouter GenAI endpoints, the new API surface, UI components, and how to run and test locally.

## 1) Architecture

- OpsML acts as a thin BFF in front of Scouter ("bifrost"). The server proxies requests to Scouter via `ScouterApiClient`.
- Handlers exchange an OpsML-permission token for a Scouter token using `exchange_token_from_perms(...)` and call `state.scouter_client.request_with_path(...)`.
- Every proxied handler inserts an `AuditContext` into the response so audit/event middleware records the read operation.
- UI components call OpsML server endpoints (not Scouter directly). The server forwards to Scouter and returns the JSON body.

Diagram (conceptual):

```
Browser UI  ->  OpsML (Axum handlers / auth middleware)
                 -> exchange token -> Scouter (bifrost) -> Scouter JSON
                 <- returns JSON to UI
```

## 2) API endpoints (new)

The server exposes lightweight proxy endpoints that the UI uses. All requests require a valid OpsML session (cookie/jwt) and are protected by the standard `auth_api_middleware`.

1) GET /api/traces/{trace_id}/genai/aggregate

- Description: Aggregate GenAI metrics for a trace (tokens, latency, model breakdown).
- Query params (optional): `start_time` (ISO), `end_time` (ISO), `interval` (minute|hour|day), `metrics` (comma-separated)
- Response (200): JSON aggregate object (example):

Request example:

```
GET /api/traces/trace-123/genai/aggregate?start_time=2026-01-01T00:00:00Z&end_time=2026-01-01T01:00:00Z
Authorization: (cookie)
```

Response example:

```json
{
  "trace_id": "trace-123",
  "total_tokens": 1500,
  "avg_latency": 120.5,
  "model_distribution": { "gpt-4o-mini": 20, "claude-3-5": 5 },
  "time_period": { "start_time": "2026-01-01T00:00:00Z", "end_time": "2026-01-01T01:00:00Z" }
}
```

2) GET /api/spans/{span_id}/genai/metrics

- Description: Span-level GenAI metrics (tokens, model, latency, cost).
- Response (200): JSON array of per-span metric objects.

Request example:

```
GET /api/spans/some-span-uid/genai/metrics
```

Response example:

```json
[
  { "token_count_input": 10, "token_count_output": 5, "model_name": "gpt-4o-mini", "latency_ms": 120, "cost": 0.0008 }
]
```

3) GET /api/services/{service_id}/genai/timeseries

- Description: Service-level GenAI timeseries and dashboard bundle (buckets, model usage, cost by model, tool metrics).
- Query params: `start_time`, `end_time`, `interval` (minute|hour|day), `metrics`
- Response (200): composite JSON (example simplified):

Request example:

```
GET /api/services/my-service/genai/timeseries?start_time=2026-01-01T00:00:00Z&end_time=2026-01-02T00:00:00Z
```

Response example (simplified):

```json
{
  "agent_dashboard": { "summary": {"total_requests": 10, "avg_duration_ms":120}, "buckets": [ {"bucket_start":"2026-01-01T00:00:00Z","total_input_tokens":100,"total_output_tokens":50,"total_cost":0.12} ] },
  "model_usage": { "models": [ {"model":"gpt-4o-mini","span_count":5} ] },
  "tool_dashboard": { "aggregates": [], "time_series": [] }
}
```

Notes
- These endpoints are proxies — the shape of the returned JSON mirrors Scouter's GenAI responses. UI components must be defensive (nulls, missing fields).
- Errors from Scouter are returned as OpsML errors (non-200 responses propagate through as 4xx/5xx).

## 3) UI components and extension points

Files added/modified (UI):

- `src/lib/components/AgentServiceDashboard/GenAIMetricsNav.svelte` — left-side nav (Overview / By Model / Token Usage / Latency) and time range controls.
- `src/lib/components/AgentServiceDashboard/GenAITimeseries.svelte` — timeseries view with four charts: tokens, latency, model usage, cost.
- `src/lib/components/TraceDetail/GenAIMetricsTab.svelte` — per-trace per-span GenAI table.
- `src/lib/components/card/agent/observability/charts.ts` — chart builders (token/latency/cost/volume) used by charts.
- `src/lib/components/card/agent/observability/GenAiChartCard.svelte` — Chart.js wrapper used by chart panels.

Extending views

- To add a new chart to the Timeseries view:
  1. Add a new builder in `charts.ts` that returns a `ChartConfiguration` for Chart.js.
  2. Import the builder into `GenAITimeseries.svelte` and construct a reactive `configFn` for `GenAiChartCard`.

Example snippet (add average latency sparkline):

```ts
// in charts.ts
export function buildAvgLatencySparkline(buckets) {
  return createTimeSeriesChart(buckets.map(b=>new Date(b.bucket_start)), buckets.map(b=>b.avg_duration_ms||0), undefined, 'avg latency', 'ms', 'line');
}

// in GenAITimeseries.svelte
import { buildAvgLatencySparkline } from '$lib/components/card/agent/observability/charts';
const latencyMiniCfg = $derived(() => buildAvgLatencySparkline(buckets));
<GenAiChartCard title="Avg Latency" configFn={latencyMiniCfg} />
```

Design notes
- Charts use Chart.js via `GenAiChartCard.svelte` and theme helpers in `src/lib/components/viz` so visual consistency is preserved.
- Prefer adding chart-builders to `charts.ts` rather than embedding Chart.js configs in components.

## 4) Running and testing locally

Prereqs
- Rust toolchain (cargo) — required to build/run OpsML server.
- Node (pnpm recommended) for the UI.
- Mise (recommended) — this repo uses `mise` task runner (see AGENTS.md / README).

Quick dev run (recommended)

1. Install mise (one-time):

```bash
curl https://mise.run | sh
mise install
```

2. Start backend + frontend (dev):

```bash
# runs backend (port 8080) and frontend (port 3000)
mise run dev:both
```

Or run frontend only (useful while backend is already running):

```bash
cd crates/opsml_server/opsml_ui
pnpm install
pnpm run dev
```

Running tests (UI)

```bash
cd crates/opsml_server/opsml_ui
pnpm install
pnpm test
```

Notes about mocks
- UI unit tests mock `createInternalApiClient` and Chart components where appropriate — see `src/lib/.../__tests__` for examples.
- If you don't have a running Scouter instance, run the UI in mock mode (dev settings) or rely on the mock endpoints used in tests.

Troubleshooting
- If `cargo` is not found, install Rust via https://rustup.rs and re-run `mise` commands.
- If charts do not render in tests, ensure the test runner has `canvas`/`jsdom` shims (the repo test config includes these shims).

## Example curl + fetch calls

Curl example (trace aggregate):

```bash
curl -v -b "<auth cookie>" "http://localhost:8080/api/traces/trace-123/genai/aggregate?start_time=2026-01-01T00:00:00Z&end_time=2026-01-01T01:00:00Z"
```

Fetch example (SvelteKit server-side code):

```ts
import { createInternalApiClient } from '$lib/api/internalClient';
const client = createInternalApiClient(fetch);
const res = await client.get(`/api/services/${serviceId}/genai/timeseries`, { start_time, end_time });
const body = await res.json();
```

## Where to look in the codebase
- Backend handlers: `crates/opsml_server/src/core/scouter/genai/route.rs`
- Router mount: `crates/opsml_server/src/core/genai_metrics/route.rs` and `crates/opsml_server/src/core/router.rs`
- UI components: `crates/opsml_server/opsml_ui/src/lib/components/AgentServiceDashboard/*`, `.../TraceDetail/GenAIMetricsTab.svelte`
- Chart builders: `crates/opsml_server/opsml_ui/src/lib/components/card/agent/observability/charts.ts`

If you want, I can add a short HOWTO showing how to add a new chart and wire a backend query end-to-end.
