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
    };
  } = $props();

  let isUpdating = $state(false);

  function determineTimeRangeFromDuration(
    startTime: DateTime,
    endTime: DateTime,
    bucketInterval: string
  ): TimeRange {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationMs = end.getTime() - start.getTime();
    const durationMinutes = durationMs / (1000 * 60);

    // Match duration to preset ranges (with some tolerance for timing differences)
    if (Math.abs(durationMinutes - 15) < 1) {
      return {
        label: 'Past 15 Minutes',
        value: '15min',
        startTime,
        endTime,
        bucketInterval,
      };
    } else if (Math.abs(durationMinutes - 30) < 1) {
      return {
        label: 'Past 30 Minutes',
        value: '30min',
        startTime,
        endTime,
        bucketInterval,
      };
    } else if (Math.abs(durationMinutes - 60) < 2) {
      return {
        label: 'Past 1 Hour',
        value: '1hour',
        startTime,
        endTime,
        bucketInterval,
      };
    } else if (Math.abs(durationMinutes - 240) < 5) {
      return {
        label: 'Past 4 Hours',
        value: '4hours',
        startTime,
        endTime,
        bucketInterval,
      };
    } else if (Math.abs(durationMinutes - 720) < 10) {
      return {
        label: 'Past 12 Hours',
        value: '12hours',
        startTime,
        endTime,
        bucketInterval,
      };
    } else if (Math.abs(durationMinutes - 1440) < 20) {
      return {
        label: 'Past 24 Hours',
        value: '24hours',
        startTime,
        endTime,
        bucketInterval,
      };
    } else if (Math.abs(durationMinutes - 10080) < 60) {
      return {
        label: 'Past 7 Days',
        value: '7days',
        startTime,
        endTime,
        bucketInterval,
      };
    } else if (Math.abs(durationMinutes - 43200) < 240) {
      return {
        label: 'Past 30 Days',
        value: '30days',
        startTime,
        endTime,
        bucketInterval,
      };
    }

    return {
      label: 'Custom Range',
      value: 'custom',
      startTime,
      endTime,
      bucketInterval,
    };
  }

  let selectedTimeRange = $state<TimeRange>(
    determineTimeRangeFromDuration(
      initialFilters.start_time,
      initialFilters.end_time,
      initialFilters.bucket_interval
    )
  );

  /**
   * Handle time range changes by updating cookies and reloading data
   */
  async function handleTimeRangeChange(range: TimeRange) {
    selectedTimeRange = range;
    isUpdating = true;

    try {
      // Write cookies client-side (matching the cookie names from +page.ts)
      setCookie('trace_start_time', range.startTime);
      setCookie('trace_end_time', range.endTime);
      setCookie('trace_bucket_interval', range.bucketInterval); // Set the NEW value from the range

      // Trigger SvelteKit to re-run the load function
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