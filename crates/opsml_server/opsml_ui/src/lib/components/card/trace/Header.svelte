<script lang="ts">
  import type { MetricType } from './types';

  interface Props {
    space?: string;
    name?: string;
    version?: string;
    selectedMetric: MetricType;
    onMetricChange: (metric: MetricType) => void;
  }

  let { space, name, version, selectedMetric, onMetricChange }: Props = $props();

  const metrics: Array<{ value: MetricType; label: string }> = [
    { value: 'trace_count', label: 'Request Count' },
    { value: 'avg_duration_ms', label: 'Avg Duration' },
    { value: 'p95_duration_ms', label: 'P95 Duration' },
    { value: 'error_rate', label: 'Error Rate' }
  ];
</script>

<header class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
  <div class="flex flex-col gap-2">
    <h1 class="text-3xl font-black uppercase tracking-tight text-gray-900">Trace Analytics</h1>
    {#if space || name}
      <div class="flex flex-wrap gap-2">
        {#if space}
          <span
            class="border-2 border-gray-900 bg-white px-3 py-1 text-sm font-semibold text-gray-900"
          >
            {space}
          </span>
        {/if}
        {#if name}
          <span
            class="border-2 border-gray-900 bg-white px-3 py-1 text-sm font-semibold text-gray-900"
          >
            {name}
          </span>
        {/if}
        {#if version}
          <span
            class="border-2 border-gray-900 bg-white px-3 py-1 text-sm font-semibold text-gray-900"
          >
            {version}
          </span>
        {/if}
      </div>
    {/if}
  </div>

  <div class="flex flex-col gap-2">
    <label for="metric-select" class="text-xs font-bold uppercase tracking-wider text-gray-700">
      Chart Metric
    </label>
    <select
      id="metric-select"
      value={selectedMetric}
      onchange={(e) => onMetricChange(e.currentTarget.value as MetricType)}
      class="border-2 border-gray-900 bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      {#each metrics as metric}
        <option value={metric.value}>{metric.label}</option>
      {/each}
    </select>
  </div>
</header>