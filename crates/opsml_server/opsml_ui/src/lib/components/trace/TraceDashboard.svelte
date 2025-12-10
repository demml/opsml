<script lang="ts">
  import type { TraceMetricBucket, TracePaginationResponse } from './types';
  import { invalidate } from '$app/navigation';
  import TraceCharts from './TraceCharts.svelte';
  import TraceTable from './TraceTable.svelte';
  import TimeRangeFilter, { type TimeRange } from './TimeRangeFilter.svelte';
  import type { DateTime } from '$lib/types';
  import {setCookie} from './utils';

  let {
    trace_page,
    trace_metrics,
    initialFilters,
  }: {
    trace_page: TracePaginationResponse;
    trace_metrics: TraceMetricBucket[];
    initialFilters: {
      start_time: DateTime;
      end_time: DateTime;
      bucket_interval: string;
      selected_range: string;
    };
  } = $props();

  let isUpdating = $state(false);

  /**
   * Initialize selected range from stored preference
   */
  let selectedTimeRange = $state<TimeRange>(
    createTimeRangeFromValue(initialFilters.selected_range)
  );

  /**
   * Create TimeRange object from a range value
   */
  function createTimeRangeFromValue(rangeValue: string): TimeRange {
    const labels: Record<string, string> = {
      '15min': 'Past 15 Minutes',
      '30min': 'Past 30 Minutes',
      '1hour': 'Past 1 Hour',
      '4hours': 'Past 4 Hours',
      '12hours': 'Past 12 Hours',
      '24hours': 'Past 24 Hours',
      '7days': 'Past 7 Days',
      '30days': 'Past 30 Days',
    };

    return {
      label: labels[rangeValue] || 'Past 15 Minutes',
      value: rangeValue,
      startTime: initialFilters.start_time,
      endTime: initialFilters.end_time,
      bucketInterval: initialFilters.bucket_interval,
    };
  }

  /**
   * Handle time range changes by storing the range value
   */
  async function handleTimeRangeChange(range: TimeRange) {
    selectedTimeRange = range;
    isUpdating = true;

    try {
      setCookie('trace_range', range.value);
      await invalidate('trace:data');
    } catch (error) {
      console.error('Failed to update time range:', error);
    } finally {
      isUpdating = false;
    }
  }
</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="flex items-center justify-between m2-4">
    <h1 class="text-2xl font-bold text-primary-800">
      Trace Dashboard
      {#if isUpdating}
        <span class="text-sm font-normal text-gray-500 ml-2">Updating...</span>
      {/if}
    </h1>
    <TimeRangeFilter
      onRangeChange={handleTimeRangeChange}
      selectedRange={selectedTimeRange}
    />
  </div>

  <div class="grid grid-cols-1 gap-4 pt-4">
    <TraceCharts buckets={trace_metrics} />
    <TraceTable trace_page={trace_page} />
  </div>
</div>