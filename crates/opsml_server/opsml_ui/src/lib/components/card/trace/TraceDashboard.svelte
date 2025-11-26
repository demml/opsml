<script lang="ts">
  import type { TraceMetricBucket, TraceFilters, TracePaginationResponse } from './types';
  import TraceCharts from './TraceCharts.svelte';
  import TraceTable from './TraceTable.svelte';
  import TimeRangeFilter, { type TimeRange } from './TimeRangeFilter.svelte';
  import type { DateTime } from '$lib/types';

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

  let selectedTimeRange = $state<TimeRange>({
    label: 'Past 15 Minutes',
    value: '15min',
    startTime: new Date(Date.now() - 15 * 60 * 1000).toISOString() as DateTime,
    endTime: new Date().toISOString() as DateTime
  });

  let filters = $state<TraceFilters>({
    space,
    name,
    version,
    limit: pageSize,
    start_time: selectedTimeRange.startTime,
    end_time: selectedTimeRange.endTime
  });

  function handleTimeRangeChange(range: TimeRange) {
    selectedTimeRange = range;
    filters = {
      ...filters,
      start_time: range.startTime,
      end_time: range.endTime
    };
    console.log('Time range changed:', range);
  }
</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-2xl font-bold text-primary-800">Trace Dashboard</h1>
    <TimeRangeFilter 
      bind:selectedRange={selectedTimeRange}
      onRangeChange={handleTimeRangeChange}
    />
  </div>

  <div class="grid grid-cols-1 gap-4 pt-4">
    <TraceCharts buckets={trace_metrics} />
    <TraceTable trace_page={trace_page} />
  </div>
</div>