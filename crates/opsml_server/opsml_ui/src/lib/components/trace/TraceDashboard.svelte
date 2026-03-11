<script lang="ts">
  import type { TraceMetricBucket, TracePaginationResponse, TimeRange, TracePageFilter, TraceMetricsRequest, TraceMetricsResponse } from './types';
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
      bucket_interval: filters.bucket_interval,
      ...filters.filters,
    };

    let traceMetrics = await getServerTraceMetrics(fetch, metricsRequest);
    return traceMetrics.metrics;
  }

  async function getTracePage(): Promise<TracePaginationResponse> {
    let request = {
      ...filters.filters,
      limit: 50,
    };
    let tracePage = await getServerTracePage(fetch, request);
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

  async function handleFiltersChange(updatedFilters: TracePageFilter) {
  if (isUpdating) return;
  isUpdating = true;

    try {
      filters = updatedFilters;
      [traceMetrics, tracePage] = await Promise.all([
        getTraceMetrics(),
        getTracePage()
      ]);

      tableKey++;
    } catch (error) {
      console.error('Failed to update filters:', error);
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

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8 space-y-6">

  <!-- Page Header -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50">
    <!-- Top bar: title + controls -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-5 py-4 border-b-2 border-black bg-white rounded-t-base">
      <div class="flex items-center gap-3">
        <div class="w-1 h-8 rounded-sm bg-primary-500 flex-shrink-0"></div>
        <div>
          <h1 class="text-2xl font-black tracking-tight text-primary-800 leading-none">
            Trace Dashboard
          </h1>
          <p class="text-xs text-gray-500 font-mono mt-0.5">
            Distributed trace observability
          </p>
        </div>

        {#if pollInterval}
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-black uppercase tracking-wide bg-error-600 text-white border-2 border-black shadow-small rounded-base animate-pulse ml-1">
            <span class="w-1.5 h-1.5 rounded-full bg-white"></span>
            Live
          </span>
        {/if}

        {#if isUpdating}
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold text-gray-600 bg-surface-200 border-2 border-black shadow-small rounded-base ml-1">
            <span class="w-3 h-3 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></span>
            Updating
          </span>
        {/if}
      </div>

      <div class="flex items-center gap-2">
        <button
          onclick={() => refreshData(false)}
          disabled={isUpdating}
          class="flex items-center gap-1.5 px-3 py-2 text-sm font-bold bg-white border-2 border-black shadow-small shadow-hover rounded-base text-primary-800 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Refresh data"
        >
          <svg class="w-3.5 h-3.5 {isUpdating ? 'animate-spin' : ''}" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>

        <TimeRangeFilter
          onRangeChange={handleTimeRangeChange}
          selectedRange={selectedTimeRange}
        />
      </div>
    </div>

    <!-- Summary stats bar -->
    <div class="grid grid-cols-2 sm:grid-cols-4 divide-x-2 divide-black rounded-b-base overflow-hidden">
      <div class="px-5 py-3">
        <div class="text-xs font-black uppercase tracking-wider text-gray-500">Loaded Traces</div>
        <div class="text-2xl font-black text-primary-800 font-mono mt-0.5">
          {tracePage.items?.length ?? '—'}
        </div>
      </div>
      <div class="px-5 py-3">
        <div class="text-xs font-black uppercase tracking-wider text-gray-500">Range</div>
        <div class="text-base font-black text-primary-800 mt-0.5 truncate">{selectedTimeRange.label}</div>
      </div>
      <div class="px-5 py-3">
        <div class="text-xs font-black uppercase tracking-wider text-gray-500">Interval</div>
        <div class="text-base font-black text-primary-800 font-mono mt-0.5">{selectedTimeRange.bucketInterval}</div>
      </div>
      <div class="px-5 py-3">
        <div class="text-xs font-black uppercase tracking-wider text-gray-500">Status</div>
        <div class="text-base font-black mt-0.5 {pollInterval ? 'text-error-600' : 'text-secondary-600'}">
          {pollInterval ? 'Live · 30s poll' : 'Static'}
        </div>
      </div>
    </div>
  </div>

  {#key tableKey}
    <!-- Charts Section -->
    <div>
      <div class="flex items-center gap-2 mb-3">
        <span class="text-xs font-black uppercase tracking-widest text-black">Metrics</span>
        <div class="flex-1 h-px bg-black opacity-10"></div>
      </div>
        <TraceCharts buckets={traceMetrics} />
    </div>
    <!-- Traces Section -->
    <div>
      <div class="flex items-center gap-2 mb-3">
        <span class="text-xs font-black uppercase tracking-widest text-black">Traces</span>
        <div class="flex-1 h-px bg-black opacity-10"></div>
      </div>
      <TraceTable
        trace_page={tracePage}
        filters={filters}
        onFiltersChange={handleFiltersChange}
      />
    </div>
  {/key}

</div>