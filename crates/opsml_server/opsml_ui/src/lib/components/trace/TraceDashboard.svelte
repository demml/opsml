<script lang="ts">
  import type {
    ActiveFilter,
    TimeRange,
    TraceFacetDimension,
    TraceFacetsResponse,
    TraceMetricBucket,
    TraceMetricsRequest,
    TraceMetricsResponse,
    TraceMode,
    TracePageFilter,
    TracePaginationResponse,
  } from "./types";
  import type { DateTime } from "$lib/types";
  import ChipBar from "./filters/ChipBar.svelte";
  import FacetSidebar from "./filters/FacetSidebar.svelte";
  import {
    derivedActiveFilters,
    removeActiveFilter,
  } from "./filters/filterState.svelte";
  import ModeTabs from "./ModeTabs.svelte";
  import TimeRangeFilter from "./TimeRangeFilter.svelte";
  import TraceCharts from "$lib/components/trace/TraceCharts.svelte";
  import TraceTable from "$lib/components/trace/TraceTable.svelte";
  import {
    calculateTimeRange,
    getServerTraceFacets,
    getServerTraceMetrics,
    getServerTracePage,
    setCookie,
  } from "./utils";

  let {
    trace_page,
    trace_metrics,
    trace_facets,
    initialFilters,
  }: {
    trace_page: TracePaginationResponse;
    trace_metrics: TraceMetricBucket[];
    trace_facets: TraceFacetsResponse;
    initialFilters: TracePageFilter;
  } = $props();

  let isUpdating = $state(false);
  let updateCounter = 0;
  let mode = $state<TraceMode>("search");
  let filters = $state<TracePageFilter>(initialFilters);
  let traceMetrics = $state<TraceMetricBucket[]>(trace_metrics);
  let tracePage = $state<TracePaginationResponse>(trace_page);
  let traceFacets = $state<TraceFacetsResponse>(trace_facets);

  const activeChips = $derived(derivedActiveFilters(filters));

  const LIVE_POLL_INTERVAL = 30_000;
  let pollInterval = $state<ReturnType<typeof setInterval> | null>(null);

  let selectedTimeRange = $state<TimeRange>(
    createTimeRangeFromValue(initialFilters.selected_range),
  );

  async function getTraceMetrics(): Promise<TraceMetricBucket[]> {
    const metricsRequest: TraceMetricsRequest = {
      bucket_interval: filters.bucket_interval,
      ...filters.filters,
    };

    const metrics: TraceMetricsResponse = await getServerTraceMetrics(
      fetch,
      metricsRequest,
    );
    return metrics.metrics;
  }

  async function getTracePage(): Promise<TracePaginationResponse> {
    return await getServerTracePage(fetch, {
      ...filters.filters,
      limit: 50,
    });
  }

  async function getTraceFacetsForRange(): Promise<TraceFacetsResponse> {
    const [serviceFacets, statusFacets] = await Promise.all([
      getServerTraceFacets(fetch, { ...filters.filters, service_name: undefined }),
      getServerTraceFacets(fetch, { ...filters.filters, status_code: undefined }),
    ]);
    return {
      services: serviceFacets.services,
      status_codes: statusFacets.status_codes,
      total_count: serviceFacets.total_count,
    };
  }

  async function refreshData() {
    const id = ++updateCounter;
    isUpdating = true;

    try {
      if (selectedTimeRange.value !== "custom") {
        const { startTime, endTime, bucketInterval } = calculateTimeRange(
          selectedTimeRange.value,
        );
        filters = {
          ...filters,
          filters: {
            ...filters.filters,
            start_time: startTime as DateTime,
            end_time: endTime as DateTime,
          },
          bucket_interval: bucketInterval,
        };
      }

      const [newMetrics, newPage, newFacets] = await Promise.all([
        getTraceMetrics(),
        getTracePage(),
        getTraceFacetsForRange(),
      ]);
      if (id !== updateCounter) return;
      traceMetrics = newMetrics;
      tracePage = newPage;
      traceFacets = newFacets;
    } catch (error) {
      console.error("Failed to refresh data:", error);
    } finally {
      if (id === updateCounter) isUpdating = false;
    }
  }

  function createTimeRangeFromValue(rangeValue: string): TimeRange {
    const labels: Record<string, string> = {
      "15min-live": "Live (15min)",
      "15min": "Past 15 Minutes",
      "30min": "Past 30 Minutes",
      "1hour": "Past 1 Hour",
      "4hours": "Past 4 Hours",
      "12hours": "Past 12 Hours",
      "24hours": "Past 24 Hours",
      "7days": "Past 7 Days",
      "30days": "Past 30 Days",
    };

    return {
      label: labels[rangeValue] || "Past 15 Minutes",
      value: rangeValue,
      startTime:
        initialFilters.filters.start_time ||
        (new Date(Date.now() - 15 * 60 * 1000).toISOString() as DateTime),
      endTime: initialFilters.filters.end_time || (new Date().toISOString() as DateTime),
      bucketInterval: initialFilters.bucket_interval,
    };
  }

  async function handleTimeRangeChange(range: TimeRange) {
    const id = ++updateCounter;
    selectedTimeRange = range;
    isUpdating = true;

    try {
      setCookie("trace_range", range.value);

      filters = {
        ...filters,
        filters: {
          ...filters.filters,
          start_time: range.startTime,
          end_time: range.endTime,
        },
        selected_range: range.value,
        bucket_interval: range.bucketInterval,
      };

      const [newMetrics, newPage, newFacets] = await Promise.all([
        getTraceMetrics(),
        getTracePage(),
        getTraceFacetsForRange(),
      ]);
      if (id !== updateCounter) return;
      traceMetrics = newMetrics;
      tracePage = newPage;
      traceFacets = newFacets;
    } catch (error) {
      console.error("Failed to update time range:", error);
    } finally {
      if (id === updateCounter) isUpdating = false;
    }
  }

  async function handleFiltersChange(updatedFilters: TracePageFilter) {
    const id = ++updateCounter;
    isUpdating = true;

    try {
      filters = updatedFilters;
      const [newMetrics, newPage, newFacets] = await Promise.all([
        getTraceMetrics(),
        getTracePage(),
        getTraceFacetsForRange(),
      ]);
      if (id !== updateCounter) return;
      traceMetrics = newMetrics;
      tracePage = newPage;
      traceFacets = newFacets;
    } catch (error) {
      console.error("Failed to update filters:", error);
    } finally {
      if (id === updateCounter) isUpdating = false;
    }
  }

  async function handleRemoveChip(chip: ActiveFilter) {
    filters = removeActiveFilter(filters, chip);
    await handleFiltersChange(filters);
  }

  function addService(service: string) {
    const next = {
      ...filters,
      filters: { ...filters.filters, service_name: service },
    };
    void handleFiltersChange(next);
  }

  function addStatus(status: number) {
    const next = {
      ...filters,
      filters: { ...filters.filters, status_code: status },
    };
    void handleFiltersChange(next);
  }

  function addHasErrors() {
    const next = {
      ...filters,
      filters: { ...filters.filters, has_errors: true },
    };
    void handleFiltersChange(next);
  }

  function addAttribute(raw: string) {
    const list = [...(filters.filters.attribute_filters ?? []), raw];
    const next = {
      ...filters,
      filters: { ...filters.filters, attribute_filters: list },
    };
    void handleFiltersChange(next);
  }

  function addDuration(min?: number, max?: number) {
    const next = {
      ...filters,
      filters: {
        ...filters.filters,
        ...(min !== undefined ? { duration_min_ms: min } : { duration_min_ms: undefined }),
        ...(max !== undefined ? { duration_max_ms: max } : { duration_max_ms: undefined }),
      },
    };
    void handleFiltersChange(next);
  }

  function setService(service: string) {
    const next = {
      ...filters,
      filters: { ...filters.filters, service_name: service },
    };
    void handleFiltersChange(next);
  }

  function clearService() {
    const nextFilters = { ...filters.filters };
    delete nextFilters.service_name;
    void handleFiltersChange({ ...filters, filters: nextFilters });
  }

  function setStatus(status: number) {
    const next = {
      ...filters,
      filters: { ...filters.filters, status_code: status },
    };
    void handleFiltersChange(next);
  }

  function clearStatus() {
    const nextFilters = { ...filters.filters };
    delete nextFilters.status_code;
    void handleFiltersChange({ ...filters, filters: nextFilters });
  }

  function toggleErrors(enabled: boolean) {
    const nextFilters = { ...filters.filters };
    if (enabled) {
      nextFilters.has_errors = true;
    } else {
      delete nextFilters.has_errors;
    }
    void handleFiltersChange({ ...filters, filters: nextFilters });
  }

  function setDuration(next: { min?: number; max?: number }) {
    void handleFiltersChange({
      ...filters,
      filters: {
        ...filters.filters,
        duration_min_ms: next.min,
        duration_max_ms: next.max,
      },
    });
  }

  function setAttributes(list: string[]) {
    const next = {
      ...filters,
      filters: { ...filters.filters, attribute_filters: list },
    };
    void handleFiltersChange(next);
  }

  $effect(() => {
    const cleanup = () => {
      if (pollInterval !== null) {
        clearInterval(pollInterval);
        pollInterval = null;
      }
    };

    if (selectedTimeRange.value === "15min-live") {
      pollInterval = setInterval(() => {
        void refreshData();
      }, LIVE_POLL_INTERVAL);
    }

    return cleanup;
  });
</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8 space-y-6">
  <div class="rounded-base border-2 border-black shadow bg-surface-50">
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
          onclick={() => void refreshData()}
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

    <div class="grid grid-cols-2 sm:grid-cols-4 divide-x-2 divide-black rounded-b-base overflow-hidden">
      <div class="px-5 py-3">
        <div class="text-xs font-black uppercase tracking-wider text-gray-500">Loaded Traces</div>
        <div class="text-2xl font-black text-primary-800 font-mono mt-0.5">
          {tracePage.items?.length ?? "—"}
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
          {pollInterval ? "Live · 30s poll" : "Static"}
        </div>
      </div>
    </div>
  </div>

  <div class="flex items-center justify-between gap-2">
    <ModeTabs {mode} onChange={(next) => (mode = next)} />
    <span class="text-xs font-mono text-gray-500">
      {mode === "search" ? "Browse traces with filters" : "Time-series analytics"}
    </span>
  </div>

  <ChipBar
    chips={activeChips}
    services={traceFacets.services.map((d) => ({ value: d.value, count: d.trace_count }))}
    statuses={traceFacets.status_codes.map((d) => ({ value: d.value, count: d.trace_count }))}
    onRemove={handleRemoveChip}
    onAddService={addService}
    onAddStatus={addStatus}
    onAddHasErrors={addHasErrors}
    onAddAttribute={addAttribute}
    onAddDuration={addDuration}
  />

  {#if mode === "search"}
    <div class="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-4">
      <FacetSidebar
        {filters}
        services={traceFacets.services.map((d: TraceFacetDimension) => ({ value: d.value, count: d.trace_count }))}
        statuses={traceFacets.status_codes.map((d: TraceFacetDimension) => ({ value: d.value, count: d.trace_count }))}
        onSetService={setService}
        onClearService={clearService}
        onSetStatus={setStatus}
        onClearStatus={clearStatus}
        onToggleErrors={toggleErrors}
        onSetDuration={setDuration}
        onSetAttributes={setAttributes}
      />

      <div class="space-y-4 min-w-0">
        <TraceCharts buckets={traceMetrics} />
      <TraceTable
        trace_page={tracePage}
        {filters}
      />
      </div>
    </div>
  {:else}
    <div>
      <div class="flex items-center gap-2 mb-3">
        <span class="text-xs font-black uppercase tracking-widest text-black">Analytics</span>
        <div class="flex-1 h-px bg-black opacity-10"></div>
      </div>
      <TraceCharts buckets={traceMetrics} />
    </div>
  {/if}
</div>
