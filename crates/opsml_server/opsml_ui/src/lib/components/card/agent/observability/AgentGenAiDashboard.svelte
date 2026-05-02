<script lang="ts">
  import { ServerPaths } from '$lib/components/api/routes';
  import { createInternalApiClient } from '$lib/api/internalClient';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import type { AgentGenAiBundle, GenAiDashboardRequest, GenAiDashboardResponse } from './types';
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

  let { bundle: initialBundle }: { bundle: AgentGenAiBundle } = $props();

  let bundle = $state<AgentGenAiBundle>(initialBundle);

  // PromptCard scope: service_name is null and entity_id is implicit on the
  // route — never let the user clear it via the FilterBar. AgentCard scope
  // owns service_name; entity_id is a freely selectable filter dimension.
  const isPromptScope = $derived(
    bundle.dashboard.applied_filters.service_name === null &&
      bundle.dashboard.applied_filters.entity_id !== null,
  );

  type FilterDelta = {
    agent_name: string | null;
    model: string | null;
    provider_name: string | null;
    operation_name: string | null;
    entity_id: string | null;
  };

  async function postDashboard(body: GenAiDashboardRequest): Promise<GenAiDashboardResponse> {
    const client = createInternalApiClient(fetch);
    const r = await client.post(ServerPaths.GENAI_DASHBOARD, body);
    if (!r.ok) throw new Error(`dashboard fetch failed: ${r.status}`);
    return (await r.json()) as GenAiDashboardResponse;
  }

  async function refetch(filters?: Partial<FilterDelta>) {
    const range = timeRangeState.selectedTimeRange;
    if (!range) return;
    const applied = bundle.dashboard.applied_filters;
    const body: GenAiDashboardRequest = {
      // service_name is route-locked (echoed verbatim from the initial bundle).
      service_name: applied.service_name,
      entity_id: filters?.entity_id !== undefined ? filters.entity_id : applied.entity_id,
      start_time: range.startTime,
      end_time: range.endTime,
      bucket_interval: range.bucketInterval,
      agent_name: filters?.agent_name ?? applied.agent_name,
      provider_name: filters?.provider_name ?? applied.provider_name,
      operation_name: filters?.operation_name ?? applied.operation_name,
      model: filters?.model ?? applied.model,
      model_pricing: {},
    };

    timeRangeState.beginRefresh();
    try {
      const dashboard = await postDashboard(body);
      bundle = {
        dashboard,
        range: {
          start_time: range.startTime,
          end_time: range.endTime,
          bucket_interval: range.bucketInterval,
          selected_range: range.value,
        },
        eval_profiles: bundle.eval_profiles,
      };
    } catch (err) {
      console.error('GenAI dashboard refetch failed:', err);
    } finally {
      timeRangeState.endRefresh();
    }
  }

  function handleFilterChange(next: FilterDelta) {
    refetch(next);
  }

  // React to time-bar driven refreshes (range change OR refresh button click).
  // Skip the initial mount: if the time bar already reflects the bundle's range
  // and refreshSignal is 0 we shouldn't double-fetch.
  let mounted = $state(false);
  $effect(() => {
    void timeRangeState.selectedTimeRange;
    void timeRangeState.refreshSignal;
    if (!mounted) {
      mounted = true;
      return;
    }
    refetch();
  });
</script>

<div class="space-y-4">
  <FilterBar
    available={bundle.dashboard.available_filters}
    applied={bundle.dashboard.applied_filters}
    evalProfiles={bundle.eval_profiles}
    lockEntity={isPromptScope}
    onChange={handleFilterChange}
  />

  <KpiRail summary={bundle.dashboard.agent_dashboard.summary} />

  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
    <VolumeChart buckets={bundle.dashboard.agent_dashboard.buckets} />
    <LatencyChart buckets={bundle.dashboard.agent_dashboard.buckets} />
    <TokenChart buckets={bundle.dashboard.agent_dashboard.buckets} />
    <CostChart costByModel={bundle.dashboard.agent_dashboard.summary.cost_by_model} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <ErrorRateChart buckets={bundle.dashboard.agent_dashboard.buckets} />
    <ToolStackChart series={bundle.dashboard.tool_dashboard.time_series} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
    <ModelsTable models={bundle.dashboard.model_usage.models} />
    <ToolsTable tools={bundle.dashboard.tool_dashboard.aggregates} />
    <ErrorsBars errors={bundle.dashboard.error_breakdown.errors} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <OperationsTable operations={bundle.dashboard.operation_breakdown.operations} />
    <AgentsTable agents={bundle.dashboard.available_filters.agents} />
  </div>
</div>
