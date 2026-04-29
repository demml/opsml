<script lang="ts">
  import "chartjs-adapter-date-fns";
  import { createStackedTraceCountChart } from "./charts";
  import MetricChart from "./MetricChart.svelte";
  import type { TraceMetricBucket } from "./types";

  let { buckets, startTime, endTime } = $props<{
    buckets: TraceMetricBucket[];
    startTime?: string;
    endTime?: string;
  }>();
</script>

<div class="w-full h-[280px]">
  <MetricChart
    configFn={() => createStackedTraceCountChart(buckets, startTime, endTime)}
    title="Traces"
  />
</div>
