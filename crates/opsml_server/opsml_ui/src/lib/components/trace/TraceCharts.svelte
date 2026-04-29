<script lang="ts">
  import "chartjs-adapter-date-fns";
  import { createStackedTraceCountChart } from "./charts";
  import MetricChart from "./MetricChart.svelte";
  import type { TraceMetricBucket } from "./types";

  let { buckets } = $props<{ buckets: TraceMetricBucket[] }>();
</script>

<div class="w-full h-[280px]">
  <MetricChart
    configFn={() => createStackedTraceCountChart(buckets)}
    title="Traces"
  />
</div>
