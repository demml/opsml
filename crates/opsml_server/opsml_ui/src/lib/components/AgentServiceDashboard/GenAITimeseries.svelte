<script lang="ts">
  import { createInternalApiClient } from '$lib/api/internalClient';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import DashboardTimeBar from '$lib/components/utils/DashboardTimeBar.svelte';
  import GenAiChartCard from '$lib/components/card/agent/observability/GenAiChartCard.svelte';
  import {
    buildTokenChart,
    buildLatencyChart,
    buildVolumeChart,
  } from '$lib/components/card/agent/observability/charts';
  import { createTimeSeriesChart } from '$lib/components/viz/timeseries';
  import { toScouterInterval } from '$lib/components/card/agent/observability/utils';
  import type {
    AgentMetricBucket,
    GenAiModelUsage,
  } from '$lib/components/card/agent/observability/types';
  import { getChartTheme, getTooltip } from '$lib/components/viz/utils';

  export let serviceId: string;

  let buckets: AgentMetricBucket[] = [];
  let models: GenAiModelUsage[] = [];
  let loading = false;
  let error: string | null = null;

  let mounted = false;
  let requestEpoch = 0;

  // Chart configs (ChartConfiguration) created reactively
  const tokenCfg = $derived(() => buildTokenChart(buckets));
  const latencyCfg = $derived(() => buildLatencyChart(buckets));
  const volumeCfg = $derived(() => buildVolumeChart(buckets));
  const costCfg = $derived(() => {
    const x = buckets.map((b) => new Date(b.bucket_start));
    const y = buckets.map((b) => b.total_cost ?? 0);
    return createTimeSeriesChart(x, y, undefined, 'cost', '$', 'line');
  });

  const modelCfg = $derived(() => {
    const theme = getChartTheme();
    const labels = models.map((m) => m.model || 'unknown');
    const data = models.map((m) => m.span_count);
    return {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'spans',
            data,
            backgroundColor: labels.map((_, i) => getChartTheme().palette?.[i % 5] ?? 'rgba(163,135,239,0.55)'),
            borderColor: labels.map((_, i) => getChartTheme().palette?.[i % 5] ?? 'rgba(163,135,239,1)'),
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { tooltip: getTooltip(), legend: { display: false } },
        scales: {
          x: { ticks: { color: theme.textColor } },
          y: { ticks: { color: theme.textColor } },
        },
      },
    } as any;
  });

  $effect(() => {
    void timeRangeState.refreshSignal;
    // trigger initial fetch only after mount — parent may provide initial data
    if (!mounted) {
      mounted = true;
      void fetchData();
    }
  });

  $effect(() => {
    // Refetch when selected range changes
    const range = timeRangeState.selectedTimeRange;
    if (!range || !mounted) return;
    void refetchForRange(range);
  });

  async function refetchForRange(range: any) {
    const epoch = ++requestEpoch;
    timeRangeState.beginRefresh();
    try {
      await fetchData(range);
      if (epoch !== requestEpoch) return;
    } catch (e) {
      if (epoch !== requestEpoch) return;
      console.error('fetch failed', e);
    } finally {
      if (epoch === requestEpoch) timeRangeState.endRefresh();
    }
  }

  async function fetchData(range?: any) {
    loading = true;
    error = null;
    try {
      const selected = range ?? timeRangeState.selectedTimeRange;
      const params: Record<string, any> = {};
      if (selected) {
        params.start_time = selected.startTime;
        params.end_time = selected.endTime;
        params.interval = toScouterInterval(selected.bucketInterval || 'hour');
      }
      const client = createInternalApiClient(fetch);
      const path = `/api/services/${encodeURIComponent(serviceId)}/genai/timeseries`;
      const res = await client.get(path, params);
      const body = await res.json();

      // Normalize to known shape: prefer agent_dashboard.buckets and model_usage.models
      buckets = (body?.agent_dashboard?.buckets ?? body?.buckets ?? []) as AgentMetricBucket[];
      models = (body?.model_usage?.models ?? body?.model_usage ?? []) as GenAiModelUsage[];
    } catch (e: any) {
      console.error('GenAI timeseries fetch error', e);
      error = e?.message ?? String(e);
    } finally {
      loading = false;
    }
  }
</script>

<div class="space-y-4">
  <div class="flex items-center justify-between">
    <h3 class="text-sm font-black uppercase tracking-wide">GenAI Timeseries</h3>
    <DashboardTimeBar
      selectedRange={timeRangeState.selectedTimeRange}
      refreshing={timeRangeState.isRefreshing}
      onRangeChange={(e) => { void refetchForRange(e.detail); }}
      onRefresh={() => { void fetchData(); }}
    />
  </div>

  {#if error}
    <div class="p-3 border-2 border-red-600 bg-red-50 rounded-base">{error}</div>
  {/if}

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <GenAiChartCard title="Tokens" subtitle="in · out · cache" height="h-48" configFn={tokenCfg} />
    <GenAiChartCard title="Latency" subtitle="p50 · p95 · p99" height="h-48" configFn={latencyCfg} />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <GenAiChartCard title="Model Usage" subtitle="spans by model" height="h-48" configFn={modelCfg} />
    <GenAiChartCard title="Cost Trend" subtitle="$ total" height="h-48" configFn={costCfg} />
  </div>
</div>

<style>
  :global(.rounded-base) { border-radius: 0.375rem; }
</style>
