<script lang="ts">
  import { Activity } from 'lucide-svelte';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import type { TimeRange } from '$lib/components/trace/types';
  import { ServerPaths } from '$lib/components/api/routes';
  import { calculateTimeRange } from '$lib/components/trace/utils';
  import type { AgentGenAiBundle } from './types';
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

  let { bundle: initialBundle }: { bundle: AgentGenAiBundle } = $props();

  let bundle = $state(initialBundle);

  const agentName = $derived((bundle.range as Record<string, unknown>).agent_name as string ?? null);

  function makeInitialRange(): TimeRange {
    const { startTime, endTime, bucketInterval } = calculateTimeRange(
      bundle.range.selected_range || '24hours',
    );
    return {
      label: bundle.range.selected_range,
      value: bundle.range.selected_range,
      startTime: startTime as TimeRange['startTime'],
      endTime: endTime as TimeRange['endTime'],
      bucketInterval,
    };
  }

  let currentRange = $state<TimeRange>(makeInitialRange());

  async function refetch(range: TimeRange) {
    const agentBody = {
      service_name: null,
      agent_name: agentName,
      provider_name: null,
      start_time: range.startTime,
      end_time: range.endTime,
      bucket_interval: range.bucketInterval,
      model_pricing: {},
    };
    const metricsBody = {
      service_name: null,
      start_time: range.startTime,
      end_time: range.endTime,
      bucket_interval: range.bucketInterval,
      operation_name: null,
      provider_name: null,
      model: null,
    };
    const toolBody = {
      service_name: null,
      start_time: range.startTime,
      end_time: range.endTime,
      bucket_interval: range.bucketInterval,
    };

    const post = (path: string, body: unknown) =>
      fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }).then((r) => r.json());

    const [agentDash, toolDash, modelUsageRes, opsRes, errsRes, agentsRes] = await Promise.all([
      post(ServerPaths.GENAI_AGENT_METRICS, agentBody),
      post(ServerPaths.GENAI_TOOL_METRICS, toolBody),
      post(ServerPaths.GENAI_MODELS, metricsBody),
      post(ServerPaths.GENAI_OPERATIONS, metricsBody),
      post(ServerPaths.GENAI_ERRORS, metricsBody),
      post(ServerPaths.GENAI_AGENTS, metricsBody),
    ]);

    bundle = {
      agent_dashboard: agentDash,
      tool_dashboard: toolDash,
      model_usage: modelUsageRes.models,
      operation_breakdown: opsRes.operations,
      errors: errsRes.errors,
      agents: agentsRes.agents,
      range: {
        start_time: range.startTime,
        end_time: range.endTime,
        bucket_interval: range.bucketInterval,
        selected_range: range.value,
      },
    };
  }

  function handleRangeChange(range: TimeRange) {
    currentRange = range;
    refetch(range);
  }
</script>

<div class="flex flex-col h-full overflow-hidden bg-surface-50">
  <header class="flex-shrink-0 flex items-center justify-between px-4 py-2.5 border-b-2 border-black bg-primary-100">
    <div class="flex items-center gap-2">
      <Activity class="w-4 h-4 text-primary-800" />
      <span class="text-sm font-black text-primary-900 uppercase tracking-wider">Agent GenAI</span>
    </div>
    <TimeRangeFilter bind:selectedRange={currentRange} onRangeChange={handleRangeChange} />
  </header>
  <div class="flex-1 overflow-y-auto overscroll-contain p-3 space-y-3">
    <KpiRail summary={bundle.agent_dashboard.summary} />
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
      <VolumeChart buckets={bundle.agent_dashboard.buckets} />
      <LatencyChart buckets={bundle.agent_dashboard.buckets} />
      <TokenChart buckets={bundle.agent_dashboard.buckets} />
      <CostChart buckets={bundle.agent_dashboard.buckets} />
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
      <ErrorRateChart buckets={bundle.agent_dashboard.buckets} />
      <ToolStackChart series={bundle.tool_dashboard.time_series} />
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
      <ModelsTable models={bundle.model_usage} />
      <ToolsTable tools={bundle.tool_dashboard.aggregates} />
      <ErrorsBars errors={bundle.errors} />
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
      <OperationsTable operations={bundle.operation_breakdown} />
      <AgentsTable agents={bundle.agents} />
    </div>
  </div>
</div>
