<script lang="ts">
  import type { GenAiTraceMetricsResponse } from '$lib/components/scouter/genai/types';
  import KpiRail from '$lib/components/card/agent/observability/KpiRail.svelte';
  import ModelsTable from '$lib/components/card/agent/observability/ModelsTable.svelte';
  import ToolsTable from '$lib/components/card/agent/observability/ToolsTable.svelte';
  import AgentsTable from '$lib/components/card/agent/observability/AgentsTable.svelte';
  import OperationsTable from '$lib/components/card/agent/observability/OperationsTable.svelte';
  import ErrorsBars from '$lib/components/card/agent/observability/ErrorsBars.svelte';
  import VolumeChart from '$lib/components/card/agent/observability/VolumeChart.svelte';
  import LatencyChart from '$lib/components/card/agent/observability/LatencyChart.svelte';
  import TokenChart from '$lib/components/card/agent/observability/TokenChart.svelte';
  import ErrorRateChart from '$lib/components/card/agent/observability/ErrorRateChart.svelte';

  let { genai }: { genai: GenAiTraceMetricsResponse } = $props();

  const buckets = $derived(genai.agent_dashboard.buckets);
</script>

<div class="flex flex-col gap-3 p-3">
  <KpiRail summary={genai.agent_dashboard.summary} />

  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
    <VolumeChart {buckets} />
    <LatencyChart {buckets} />
    <TokenChart {buckets} />
    <ErrorRateChart {buckets} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
    <ModelsTable models={genai.model_usage.models} />
    <ToolsTable tools={genai.tool_dashboard.aggregates} />
    <AgentsTable agents={genai.agent_activity.agents} />
  </div>

  {#if genai.operation_breakdown.operations.length > 0}
    <OperationsTable operations={genai.operation_breakdown.operations} />
  {/if}

  {#if genai.error_breakdown.errors.length > 0}
    <ErrorsBars errors={genai.error_breakdown.errors} />
  {/if}
</div>
