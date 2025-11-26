<script lang="ts">
  import type { TraceListItem, TraceMetricBucket, TraceFilters, TracePaginationResponse } from './types';
  import TraceCharts from './TraceCharts.svelte';
  import TraceTable from './TraceTable.svelte';

  let {
    space,
    name,
    version,
    trace_page,
    trace_metrics
  }: {
    space?: string;
    name?: string;
    version?: string;
    trace_page: TracePaginationResponse;
    trace_metrics: TraceMetricBucket[];
  } = $props();

 
  const pageSize = 50;

  let filters = $state<TraceFilters>({
    space,
    name,
    version,
    limit: pageSize
  });


</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="grid grid-cols-1 gap-4 pt-4">
    <TraceCharts buckets={trace_metrics} />
    <TraceTable trace_page={trace_page} />
  </div>
</div>