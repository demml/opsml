<script lang="ts">
  import type { TraceMetricBucket, TracePaginationResponse, TimeRange, TracePageFilter, TraceMetricsRequest, TraceMetricsResponse } from './types';
  import { invalidate } from '$app/navigation';
  import TraceCharts from './TraceCharts.svelte';
  import TraceTable from './TraceTable.svelte';
  import TimeRangeFilter from './TimeRangeFilter.svelte';
  import type { DateTime } from '$lib/types';
  import {setCookie} from './utils';
  import { getServerTraceMetrics, getServerTracePage } from './utils';

  let {
    trace_page,
    trace_metrics,
    initialFilters,
  }: {
    trace_page: TracePaginationResponse;
    trace_metrics: TraceMetricBucket[];
    initialFilters: TracePageFilter;
  } = $props();

  let isUpdating = $state(false);
  let tableKey = $state(0);
  let filters = $state<TracePageFilter>(initialFilters);
  let traceMetrics = $state<TraceMetricBucket[]>(trace_metrics);
  let tracePage = $state<TracePaginationResponse>(trace_page);

  // Polling configuration
  const LIVE_POLL_INTERVAL = 30_000; // Poll every 30 seconds
  let pollInterval = $state<ReturnType<typeof setInterval> | null>(null);

  async function getTraceMetrics(): Promise<TraceMetricBucket[]> {
    const metricsRequest: TraceMetricsRequest = {
      service_name: filters.filters.service_name,
      start_time: filters.filters.start_time || '',
      end_time: filters.filters.end_time || '',
      bucket_interval: filters.bucket_interval,
    };

    let traceMetrics = await getServerTraceMetrics(fetch, metricsRequest);
    return traceMetrics.metrics;
  }

  async function getTracePage(): Promise<TracePaginationResponse> {
    let tracePage = await getServerTracePage(fetch, {
      ...filters.filters,
      limit: 50,
    });
    return tracePage;
  }

  /**
   * Refresh data - updates time range if in live mode
   */
  async function refreshData(isLiveUpdate = false) {
    if (isUpdating) return;
    isUpdating = true;

    try {
      // If live mode, update the time range to current time
      if (isLiveUpdate && selectedTimeRange.value === '15min-live') {
        const now = new Date();
        const fifteenMinutesAgo = new Date(now.getTime() - 15 * 60 * 1000);

        filters = {
          ...filters,
          filters: {
            ...filters.filters,
            start_time: fifteenMinutesAgo.toISOString() as DateTime,
            end_time: now.toISOString() as DateTime,
          },
        };
      }
      [traceMetrics, tracePage] = await Promise.all([
        getTraceMetrics(),
        getTracePage()
      ]);

      tableKey++;

    } catch (error) {
      console.error('Failed to refresh data:', error);
    } finally {
      isUpdating = false;
    }
  }

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
      '15min-live': 'Live (15min)',
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
      startTime: initialFilters.filters.start_time || (new Date(Date.now() - 15 * 60 * 1000).toISOString() as DateTime),
      endTime: initialFilters.filters.end_time || (new Date().toISOString() as DateTime),
      bucketInterval: initialFilters.bucket_interval,
    };
  }

  /**
   * Handle time range changes by storing the range value
   */
  async function handleTimeRangeChange(range: TimeRange) {
    // Stop any existing polling
    selectedTimeRange = range;
    isUpdating = true;

    try {
      setCookie('trace_range', range.value);

      filters = {
        ...filters,
        filters: {
          ...filters.filters,
          start_time: range.startTime,
          end_time: range.endTime,
        },
        selected_range: range.value,
      };

      [traceMetrics, tracePage] = await Promise.all([
        getTraceMetrics(),
        getTracePage()
      ]);

      tableKey++;

    } catch (error) {
      console.error('Failed to update time range:', error);
    } finally {
      isUpdating = false;
    }
  }

  $effect(() => {

    const cleanup = () => {
      if (pollInterval !== null) {
        clearInterval(pollInterval);
        pollInterval = null;
        console.log('⏸️ Stopping live polling (via effect cleanup)');
      }
    };

    if (selectedTimeRange.value === '15min-live') {
      console.log('🔴 Starting live polling (30s interval)');
      pollInterval = setInterval(() => {
        refreshData(true);
      }, LIVE_POLL_INTERVAL);
    }

  return cleanup;
});
</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="flex items-center justify-between m2-4">
    <h1 class="text-2xl font-bold text-primary-800 inline-flex items-center">
      Trace Dashboard
      {#if isUpdating}
        <span class="text-sm font-normal text-gray-500 ml-2">Updating...</span>
      {/if}
      {#if pollInterval}
        <span class="inline-flex items-center gap-1 ml-2 px-2 py-1 text-xs font-bold bg-error-600 text-white rounded-full animate-pulse">
          🔴 LIVE
        </span>
      {/if}
    </h1>
    <TimeRangeFilter
      onRangeChange={handleTimeRangeChange}
      selectedRange={selectedTimeRange}
    />
  </div>

  <div class="grid grid-cols-1 gap-4 pt-4">
    {#key tableKey}
      <TraceCharts buckets={traceMetrics} />
      <TraceTable
        trace_page={tracePage}
        filters={filters}
      />
    {/key}
  </div>
</div>