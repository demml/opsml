<script lang="ts">
  import { ServerPaths } from '$lib/components/api/routes';
  import { createInternalApiClient } from '$lib/api/internalClient';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import type {
    AgentGenAiBundle,
    GenAiDashboardRequest,
    GenAiDashboardResponse,
  } from './types';
  import KpiRail from './KpiRail.svelte';
  import VolumeChart from './VolumeChart.svelte';
  import LatencyChart from './LatencyChart.svelte';
  import TokenChart from './TokenChart.svelte';
  import CostChart from './CostChart.svelte';
  import ErrorRateChart from './ErrorRateChart.svelte';
  import ToolStackChart from './ToolStackChart.svelte';
  import ModelsTable from './ModelsTable.svelte';
  import ToolsTable from './ToolsTable.svelte';
  import ErrorsBars from './ErrorsBars.svelte';
  import OperationsTable from './OperationsTable.svelte';
  import AgentsTable from './AgentsTable.svelte';
  import FilterBar from './FilterBar.svelte';
  import { toScouterInterval } from './utils';

  let { bundle: initialBundle }: { bundle: AgentGenAiBundle } = $props();

  // Eval profiles are determined by the parent route layout. They never change
  // for the lifetime of this component, so they live as a constant — not in
  // $state — and don't participate in reactivity.
  const evalProfiles = initialBundle.eval_profiles;

  // ── Input state ────────────────────────────────────────────────────────────
  // The filters that drive the fetch. Mutating any field re-fires the effect.
  // Service identity fields are route-locked (set on mount, never change via the UI).
  // entity_id is route-locked when isPromptScope; otherwise user-selectable.
  let filters = $state({
    service_name: initialBundle.dashboard.applied_filters.service_name,
    service_namespace: initialBundle.dashboard.applied_filters.service_namespace,
    service_version: initialBundle.dashboard.applied_filters.service_version,
    service_instance_id: initialBundle.dashboard.applied_filters.service_instance_id,
    entity_id: initialBundle.dashboard.applied_filters.entity_id,
    agent_name: initialBundle.dashboard.applied_filters.agent_name,
    provider_name: initialBundle.dashboard.applied_filters.provider_name,
    operation_name: initialBundle.dashboard.applied_filters.operation_name,
    model: initialBundle.dashboard.applied_filters.model,
  });

  // PromptCard scope: service_name is null and entity_id is implicit on the
  // route — the FilterBar locks the Profile dropdown so it can't be cleared.
  const isPromptScope = $derived(
    filters.service_name === null && filters.entity_id !== null,
  );

  // ── Output state ───────────────────────────────────────────────────────────
  // Server response cache. NEVER read inside the fetch effect — doing so
  // would make the effect depend on its own output and self-trigger.
  let dashboard = $state<GenAiDashboardResponse>(initialBundle.dashboard);

  // ── Fetch orchestration ────────────────────────────────────────────────────
  // Skip the fetch on initial mount: the loader-provided bundle already
  // matches the current filter+range state. `requestEpoch` lets late
  // responses from superseded requests be discarded so out-of-order
  // network completion can never overwrite fresher data.
  let mounted = false;
  let requestEpoch = 0;

  $effect(() => {
    // Read every reactive input synchronously so Svelte registers it as a
    // dependency of this effect. None of these reads touch `dashboard`, so
    // the effect cannot re-fire on its own output.
    const range = timeRangeState.selectedTimeRange;
    void timeRangeState.refreshSignal;
    const snapshot = {
      service_name: filters.service_name,
      service_namespace: filters.service_namespace,
      service_version: filters.service_version,
      service_instance_id: filters.service_instance_id,
      entity_id: filters.entity_id,
      agent_name: filters.agent_name,
      provider_name: filters.provider_name,
      operation_name: filters.operation_name,
      model: filters.model,
    };

    if (!mounted) {
      mounted = true;
      return;
    }
    if (!range) return;

    const epoch = ++requestEpoch;
    const body: GenAiDashboardRequest = {
      ...snapshot,
      start_time: range.startTime,
      end_time: range.endTime,
      bucket_interval: toScouterInterval(range.bucketInterval),
      model_pricing: {},
    };

    void runFetch(body, epoch);
  });

  async function runFetch(body: GenAiDashboardRequest, epoch: number) {
    timeRangeState.beginRefresh();
    try {
      const next = await postDashboard(body);
      if (epoch !== requestEpoch) return;
      dashboard = next;
    } catch (err) {
      if (epoch !== requestEpoch) return;
      console.error('GenAI dashboard refetch failed:', err);
    } finally {
      if (epoch === requestEpoch) timeRangeState.endRefresh();
    }
  }

  async function postDashboard(body: GenAiDashboardRequest): Promise<GenAiDashboardResponse> {
    const client = createInternalApiClient(fetch);
    const r = await client.post(ServerPaths.GENAI_DASHBOARD, body);
    if (!r.ok) throw new Error(`dashboard fetch failed: ${r.status}`);
    return (await r.json()) as GenAiDashboardResponse;
  }

  function handleFilterChange(next: {
    agent_name: string | null;
    model: string | null;
    provider_name: string | null;
    operation_name: string | null;
    entity_id: string | null;
  }) {
    filters = {
      service_name: filters.service_name,
      service_namespace: filters.service_namespace,
      service_version: filters.service_version,
      service_instance_id: filters.service_instance_id,
      entity_id: isPromptScope ? filters.entity_id : next.entity_id,
      agent_name: next.agent_name,
      provider_name: next.provider_name,
      operation_name: next.operation_name,
      model: next.model,
    };
  }
</script>

<div class="space-y-4">
  <FilterBar
    available={dashboard.available_filters}
    applied={dashboard.applied_filters}
    {evalProfiles}
    lockEntity={isPromptScope}
    onChange={handleFilterChange}
  />

  <KpiRail summary={dashboard.agent_dashboard.summary} />

  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
    <VolumeChart buckets={dashboard.agent_dashboard.buckets} />
    <LatencyChart buckets={dashboard.agent_dashboard.buckets} />
    <TokenChart buckets={dashboard.agent_dashboard.buckets} />
    <CostChart costByModel={dashboard.agent_dashboard.summary.cost_by_model} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <ErrorRateChart buckets={dashboard.agent_dashboard.buckets} />
    <ToolStackChart series={dashboard.tool_dashboard.time_series} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
    <ModelsTable models={dashboard.model_usage.models} />
    <ToolsTable tools={dashboard.tool_dashboard.aggregates} />
    <ErrorsBars errors={dashboard.error_breakdown.errors} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <OperationsTable operations={dashboard.operation_breakdown.operations} />
    <AgentsTable agents={dashboard.available_filters.agents} />
  </div>
</div>
