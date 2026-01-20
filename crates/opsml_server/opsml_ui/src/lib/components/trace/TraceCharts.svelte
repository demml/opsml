<script lang="ts">
  import type {  TraceMetricBucket } from './types';
  import { createTraceCountChart, createLatencyChart, createErrorRateChart } from './charts';
  import 'chartjs-adapter-date-fns';
  import MetricChart from './MetricChart.svelte';

  let { buckets } = $props<{ buckets: TraceMetricBucket[] }>();

</script>


<div class="grid grid-cols-1 lg:grid-cols-3 gap-4 w-full">
  <MetricChart
      config={createTraceCountChart(buckets)}
      title="Total Traces"
  />

  <MetricChart
      config={createErrorRateChart(buckets)}
      title="Error Rate (%)"
  />

  <MetricChart
      config={createLatencyChart(buckets)}
      title="Latency (ms)"
  />
</div>