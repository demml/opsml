<script lang="ts">
  import TraceDetailSidebar from "./TraceDetailSidebar.svelte";
  import TraceInfiniteScroll from "./TraceInfiniteScroll.svelte";
  import { getServerTraceSpans } from "./utils";
  import type {
    TraceListItem,
    TracePageFilter,
    TracePaginationResponse,
    TraceSpansResponse,
  } from "./types";

  let {
    trace_page,
    filters,
    initialTrace,
    initialTraceSpans,
  } = $props<{
    trace_page: TracePaginationResponse;
    filters: TracePageFilter;
    initialTrace?: TraceListItem;
    initialTraceSpans?: TraceSpansResponse;
  }>();

  let selectedTraceSpans = $state<TraceSpansResponse | null>(initialTraceSpans ?? null);
  let selectedTrace = $state<TraceListItem | null>(initialTrace ?? null);
  let isLoadingDetail = $state(false);

  const maxDurationInPage = $derived(
    Math.max(
      1,
      ...((trace_page.items ?? []).map((trace: TraceListItem) => trace.duration_ms ?? 0)),
    ),
  );

  async function handleTraceClick(trace: TraceListItem) {
    isLoadingDetail = true;
    try {
      const spans = await getServerTraceSpans(fetch, {
        trace_id: trace.trace_id,
        service_name: trace.service_name,
        start_time: trace.start_time,
        end_time: trace.end_time ?? undefined,
      });

      if (spans) {
        selectedTraceSpans = spans;
        selectedTrace = trace;
      }
    } catch (error) {
      console.error("Failed to load trace details:", error);
    } finally {
      isLoadingDetail = false;
    }
  }

  function handleClosePanel() {
    selectedTraceSpans = null;
    selectedTrace = null;
  }

  function formatTimestamp(timestamp: string | number): string {
    const date = new Date(timestamp);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    });
  }

  function formatDuration(durationMs: number | null | undefined): string {
    if (durationMs === null || durationMs === undefined) return "N/A";
    if (durationMs < 1) return `${(durationMs * 1000).toFixed(0)}μs`;
    if (durationMs < 1000) return `${durationMs.toFixed(0)}ms`;
    if (durationMs < 60000) return `${(durationMs / 1000).toFixed(2)}s`;
    return `${(durationMs / 60000).toFixed(2)}m`;
  }

  function getStatusColor(statusCode: number): string {
    if (statusCode === 1) return "bg-secondary-500";
    if (statusCode === 0) return "bg-warning-500";
    if (statusCode === 2) return "bg-error-600";
    return "bg-surface-400";
  }

  function getDurationBarWidth(durationMs: number | null): number {
    const duration = durationMs ?? 0;
    const ratio = duration / maxDurationInPage;
    return Math.max(4, Math.min(56, ratio * 56));
  }
</script>

<div class="flex flex-col rounded-base border-2 border-black shadow overflow-hidden">
  <div class="flex items-center justify-between px-4 py-2.5 bg-primary-500 border-b-2 border-black">
    <span class="font-black text-sm uppercase tracking-wide text-white">Traces</span>
    <span class="text-xs font-mono text-primary-100">click a row to inspect</span>
  </div>

  <div class="flex-1 flex flex-col bg-surface-50 overflow-x-auto">
    <div class="h-full flex flex-col min-w-[900px]">
      <div class="bg-surface-100 border-b-2 border-black sticky top-0 z-5">
        <div class="grid grid-cols-[64px_180px_1fr_1fr_100px_100px_80px_120px] gap-2 text-black text-xs font-black uppercase tracking-wide px-3 py-2">
          <div class="text-center text-black">ID</div>
          <div class="text-left">
            <span class="px-2 py-0.5 rounded-base bg-primary-100 text-primary-800 border border-primary-300">Date</span>
          </div>
          <div class="text-left">
            <span class="px-2 py-0.5 rounded-base bg-primary-100 text-primary-800 border border-primary-300">Service</span>
          </div>
          <div class="text-left">
            <span class="px-2 py-0.5 rounded-base bg-primary-100 text-primary-800 border border-primary-300">Resource</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-0.5 rounded-base bg-primary-100 text-primary-800 border border-primary-300">Duration</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-0.5 rounded-base bg-primary-100 text-primary-800 border border-primary-300">Method</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-0.5 rounded-base bg-primary-100 text-primary-800 border border-primary-300">Spans</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-0.5 rounded-base bg-primary-100 text-primary-800 border border-primary-300">Status</span>
          </div>
        </div>
      </div>

      <div class="flex-1 bg-surface-50 overflow-y-auto">
        <TraceInfiniteScroll initialPage={trace_page} {filters} height="800px">
          {#snippet children(trace: TraceListItem, index: number)}
            <div
              class="grid grid-cols-[64px_180px_1fr_1fr_100px_100px_80px_120px] gap-2 items-center px-3 py-2.5 border-b border-black hover:bg-primary-100 cursor-pointer transition-colors {index % 2 === 0 ? 'bg-surface-50' : 'bg-surface-100'}"
              onclick={() => handleTraceClick(trace)}
              onkeydown={(event) => event.key === "Enter" && handleTraceClick(trace)}
              role="button"
              tabindex="0"
            >
              <div class="text-center">
                <span class="text-xs font-mono text-black bg-surface-200 px-1.5 py-0.5 rounded">{trace.trace_id.slice(0, 7)}</span>
              </div>

              <div class="flex items-center gap-2 min-w-0">
                <div
                  class="h-3 rounded-sm border-2 border-black flex-shrink-0 {trace.has_errors ? 'bg-error-600' : 'bg-secondary-500'}"
                  style="width: {getDurationBarWidth(trace.duration_ms)}px;"
                  title={`${trace.duration_ms ?? 0}ms`}
                ></div>
                <span class="text-xs text-black font-mono truncate">{formatTimestamp(trace.start_time)}</span>
              </div>

              <div class="flex items-center gap-2 min-w-0">
                <span class="inline-block w-2 h-2 rounded-full bg-primary-500 flex-shrink-0"></span>
                <span class="text-xs text-black truncate">{trace.service_name ?? "Unknown"}</span>
              </div>

              <div class="min-w-0">
                <span class="text-xs text-black truncate block">{trace.root_operation ?? "N/A"}</span>
              </div>

              <div class="text-center">
                <span class="text-xs text-black font-mono">{formatDuration(trace.duration_ms)}</span>
              </div>

              <div class="text-center">
                <span class="px-2 py-0.5 rounded-base bg-surface-200 border border-black text-black text-xs font-bold">
                  {trace.scope ?? "GET"}
                </span>
              </div>

              <div class="text-center">
                <span class="text-xs text-black font-mono font-bold">{trace.span_count ?? 0}</span>
              </div>

              <div class="text-center">
                <span class="inline-block px-2 py-0.5 rounded-base border border-black text-white text-xs font-black {getStatusColor(trace.status_code)}">
                  {trace.status_code}
                </span>
              </div>
            </div>
          {/snippet}
        </TraceInfiniteScroll>
      </div>
    </div>
  </div>
</div>

{#if selectedTraceSpans && selectedTrace}
  <TraceDetailSidebar
    trace={selectedTrace}
    traceSpans={selectedTraceSpans}
    onClose={handleClosePanel}
  />
{/if}

{#if isLoadingDetail}
  <div class="fixed inset-0 bg-black/20 z-50 flex items-center justify-center">
    <div class="bg-surface-50 border-2 border-black rounded-base shadow p-6 flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-3 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-sm font-black text-primary-800 uppercase tracking-wide">Loading trace details</p>
    </div>
  </div>
{/if}
