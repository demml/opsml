<script lang="ts">
  import { replaceState } from "$app/navigation";
  import { resolve } from "$app/paths";
  import type {
    TimeRange,
    TraceFacetDimension,
    TraceFacetsResponse,
    TraceListItem,
    TraceMetricBucket,
    TraceMetricsRequest,
    TraceMetricsResponse,
    TraceMode,
    TracePageFilter,
    TracePaginationResponse,
    TraceSpansResponse,
  } from "./types";
  import {
    addToClause,
    attrClause,
    durationMaxClause,
    durationMinClause,
    hasErrorsClause,
    removeClauseDimension,
    replaceClauseDimension,
    serviceClause,
    serviceInstanceIdClause,
    serviceNamespaceClause,
    serviceVersionClause,
    statusCodeClause,
    type ActiveFilter,
    type FilterClause,
  } from "./clause";
  import type { DateTime } from "$lib/types";
  import ChipBar from "./filters/ChipBar.svelte";
  import FacetSidebar from "./filters/FacetSidebar.svelte";
  import {
    derivedActiveFilters,
    removeActiveFilter,
  } from "./filters/filterState.svelte";
  import ModeTabs from "./ModeTabs.svelte";
  import DashboardTimeBar from "$lib/components/utils/DashboardTimeBar.svelte";
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
    initialTrace,
    initialTraceSpans,
    mockMode = false,
  }: {
    trace_page: TracePaginationResponse;
    trace_metrics: TraceMetricBucket[];
    trace_facets: TraceFacetsResponse;
    initialFilters: TracePageFilter;
    initialTrace?: TraceListItem;
    initialTraceSpans?: TraceSpansResponse;
    mockMode?: boolean;
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
      start_time: filters.filters.start_time ?? selectedTimeRange.startTime,
      end_time: filters.filters.end_time ?? selectedTimeRange.endTime,
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
      getServerTraceFacets(fetch, {
        ...filters.filters,
        clause: removeClauseDimension(filters.filters.clause, "service"),
      }),
      getServerTraceFacets(fetch, {
        ...filters.filters,
        clause: removeClauseDimension(filters.filters.clause, "status_code"),
      }),
    ]);
    return {
      services: serviceFacets.services,
      namespaces: [],
      versions: [],
      instance_ids: [],
      status_codes: statusFacets.status_codes,
      total_count: serviceFacets.total_count,
    };
  }

  function stripTraceIdFromUrl() {
    const url = new URL(window.location.href);
    if (url.searchParams.has("trace_id")) {
      url.searchParams.delete("trace_id");
      replaceState(resolve((url.pathname + url.search) as `/opsml/${string}`), history.state);
    }
  }

  async function refreshData() {
    const id = ++updateCounter;
    isUpdating = true;
    stripTraceIdFromUrl();

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
      "custom": "Custom Range",
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
    stripTraceIdFromUrl();

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
    updateClause(replaceClauseDimension(filters.filters.clause, "service", serviceClause(service)));
  }

  function addStatus(status: number) {
    updateClause(replaceClauseDimension(filters.filters.clause, "status_code", statusCodeClause(status)));
  }

  function addHasErrors() {
    updateClause(replaceClauseDimension(filters.filters.clause, "has_errors", hasErrorsClause(true)));
  }

  function addAttribute(raw: string) {
    const [key, ...rest] = raw.split("=");
    const value = rest.join("=");
    if (!key.trim() || !value.trim()) return;
    updateClause(addToClause(filters.filters.clause, attrClause(key.trim(), value.trim())));
  }

  function addDuration(min?: number, max?: number) {
    let clause = removeClauseDimension(filters.filters.clause, "duration");
    if (min !== undefined) clause = addToClause(clause, durationMinClause(min));
    if (max !== undefined) clause = addToClause(clause, durationMaxClause(max));
    updateClause(clause);
  }

  function setService(service: string) {
    updateClause(replaceClauseDimension(filters.filters.clause, "service", serviceClause(service)));
  }

  function clearService() {
    updateClause(removeClauseDimension(filters.filters.clause, "service"));
  }

  function setNamespace(namespace: string) {
    updateClause(
      replaceClauseDimension(
        filters.filters.clause,
        "service_namespace",
        serviceNamespaceClause(namespace),
      ),
    );
  }

  function clearNamespace() {
    updateClause(removeClauseDimension(filters.filters.clause, "service_namespace"));
  }

  function setVersion(version: string) {
    updateClause(
      replaceClauseDimension(
        filters.filters.clause,
        "service_version",
        serviceVersionClause(version),
      ),
    );
  }

  function clearVersion() {
    updateClause(removeClauseDimension(filters.filters.clause, "service_version"));
  }

  function setInstance(instanceId: string) {
    updateClause(
      replaceClauseDimension(
        filters.filters.clause,
        "service_instance_id",
        serviceInstanceIdClause(instanceId),
      ),
    );
  }

  function clearInstance() {
    updateClause(removeClauseDimension(filters.filters.clause, "service_instance_id"));
  }

  function setStatus(status: number) {
    updateClause(replaceClauseDimension(filters.filters.clause, "status_code", statusCodeClause(status)));
  }

  function clearStatus() {
    updateClause(removeClauseDimension(filters.filters.clause, "status_code"));
  }

  function toggleErrors(enabled: boolean) {
    updateClause(
      replaceClauseDimension(
        filters.filters.clause,
        "has_errors",
        enabled ? hasErrorsClause(true) : undefined,
      ),
    );
  }

  function setDuration(next: { min?: number; max?: number }) {
    let clause = removeClauseDimension(filters.filters.clause, "duration");
    if (next.min !== undefined) clause = addToClause(clause, durationMinClause(next.min));
    if (next.max !== undefined) clause = addToClause(clause, durationMaxClause(next.max));
    updateClause(clause);
  }

  function setAttributes(list: string[]) {
    let clause = removeClauseDimension(filters.filters.clause, "attr");
    for (const raw of list) {
      const [key, ...rest] = raw.split("=");
      const value = rest.join("=");
      if (key.trim() && value.trim()) {
        clause = addToClause(clause, attrClause(key.trim(), value.trim()));
      }
    }
    updateClause(clause);
  }

  function updateClause(clause: FilterClause | undefined) {
    void handleFiltersChange({
      ...filters,
      filters: {
        ...filters.filters,
        clause,
      },
    });
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

      <DashboardTimeBar
        selectedRange={selectedTimeRange}
        refreshing={isUpdating}
        onRangeChange={handleTimeRangeChange}
        onRefresh={() => void refreshData()}
      />
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
        namespaces={(traceFacets.namespaces ?? []).map((d: TraceFacetDimension) => ({ value: d.value, count: d.trace_count }))}
        versions={(traceFacets.versions ?? []).map((d: TraceFacetDimension) => ({ value: d.value, count: d.trace_count }))}
        instances={(traceFacets.instance_ids ?? []).map((d: TraceFacetDimension) => ({ value: d.value, count: d.trace_count }))}
        statuses={traceFacets.status_codes.map((d: TraceFacetDimension) => ({ value: d.value, count: d.trace_count }))}
        onSetService={setService}
        onClearService={clearService}
        onSetNamespace={setNamespace}
        onClearNamespace={clearNamespace}
        onSetVersion={setVersion}
        onClearVersion={clearVersion}
        onSetInstance={setInstance}
        onClearInstance={clearInstance}
        onSetStatus={setStatus}
        onClearStatus={clearStatus}
        onToggleErrors={toggleErrors}
        onSetDuration={setDuration}
        onSetAttributes={setAttributes}
      />

      <div class="space-y-4 min-w-0">
        {#key traceMetrics}
          <TraceCharts
            buckets={traceMetrics}
            startTime={filters.filters.start_time}
            endTime={filters.filters.end_time}
          />
        {/key}
      <TraceTable
        trace_page={tracePage}
        {filters}
        {initialTrace}
        {initialTraceSpans}
        {mockMode}
      />
      </div>
    </div>
  {:else}
    <div>
      <div class="flex items-center gap-2 mb-3">
        <span class="text-xs font-black uppercase tracking-widest text-black">Analytics</span>
        <div class="flex-1 h-px bg-black opacity-10"></div>
      </div>
      {#key traceMetrics}
        <TraceCharts
          buckets={traceMetrics}
          startTime={filters.filters.start_time}
          endTime={filters.filters.end_time}
        />
      {/key}
    </div>
  {/if}
</div>
