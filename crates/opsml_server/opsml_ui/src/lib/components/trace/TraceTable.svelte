<script lang="ts">
  import type { TraceListItem, TracePaginationResponse, TraceSpansResponse, } from './types';
  import TraceDetailSidebar from './TraceDetailSidebar.svelte';
  import TraceInfiniteScroll from './TraceInfiniteScroll.svelte';
  import { getServerTraceSpans } from './utils';
  import type { TracePageFilter } from './types';
  import MultiComboSearchBox from '../utils/MultiComboSearchBox.svelte';

  let {
    trace_page,
    filters,
    onFiltersChange
  } = $props<{
    trace_page: TracePaginationResponse,
    filters: TracePageFilter,
    onFiltersChange: (updatedFilters: TracePageFilter) => void
  }>();
  let filteredAttributes: string[] = $state(filters.filters.attribute_filters || []);
  let selectedTraceSpans= $state<TraceSpansResponse | null>(null);
  let selectedTrace = $state<TraceListItem | null>(null);
  let isLoadingDetail = $state(false);

  /**
   * Handle trace row click - fetch trace details and show panel
   */
  async function handleTraceClick(trace: TraceListItem) {
    isLoadingDetail = true;
    try {
      const spans = await getServerTraceSpans(fetch, { trace_id: trace.trace_id });

      if (spans) {
        selectedTraceSpans = spans;
        selectedTrace = trace;
      }
    } catch (error) {
      console.error('Failed to load trace details:', error);
    } finally {
      isLoadingDetail = false;
    }
  }

  function handleClosePanel() {
    selectedTraceSpans = null;
    selectedTrace = null;
  }

  /**
   * Format timestamp for display
   */
  function formatTimestamp(timestamp: string | number): string {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  }

  /**
   * Format duration in milliseconds to human-readable string
   */
  function formatDuration(durationMs: number | null | undefined): string {
    if (durationMs === null || durationMs === undefined) return 'N/A';
    if (durationMs < 1) return `${(durationMs * 1000).toFixed(0)}μs`;
    if (durationMs < 1000) return `${durationMs.toFixed(0)}ms`;
    if (durationMs < 60000) return `${(durationMs / 1000).toFixed(2)}s`;
    return `${(durationMs / 60000).toFixed(2)}m`;
  }

  /**
   * Get Tailwind color class based on HTTP status code
   */
  export function getStatusColor(statusCode: number): string {
    if (statusCode == 1) return "bg-secondary-500";
    if (statusCode == 0) return "bg-warning-500";
    if (statusCode == 2) return "bg-error-600";
    return "bg-gray-400";
  }

  // update filters.tags when filteredTags changes
  function handleAttributeFilterChange(attribute_filters: string[]) {
    filters.filters.attribute_filters = attribute_filters;
    onFiltersChange(filters);
  }


</script>

<div class="grid grid-cols-1 lg:grid-cols-5 gap-4">

  <!-- Filter Sidebar -->
  <div class="col-span-1 lg:col-span-1 flex flex-col rounded-base border-2 border-black shadow bg-surface-50 self-start overflow-hidden">
    <div class="flex flex-col px-3 py-2.5 border-b-2 border-black bg-white gap-1">
      <span class="text-xs font-black uppercase tracking-widest text-gray-500">Filters</span>
      <span class="text-xs font-mono text-gray-400"><span class="text-primary-700">key:value</span> or <span class="text-primary-700">key=value</span></span>
    </div>
    <div class="p-2">
      <MultiComboSearchBox
        boxId="attribute-search-input"
        label="Search Attributes"
        filteredItems={filteredAttributes}
        onItemsChange={handleAttributeFilterChange}
      />
    </div>
  </div>

  <!-- Trace Table -->
  <div class="col-span-1 lg:col-span-4 flex flex-col rounded-base border-2 border-black shadow overflow-hidden">
    <!-- Table Header -->
    <div class="flex items-center justify-between px-4 py-2.5 bg-primary-500 border-b-2 border-black">
      <span class="font-black text-sm uppercase tracking-wide text-white">Traces</span>
      <span class="text-xs font-mono text-primary-100">click a row to inspect</span>
    </div>

    <div class="flex-1 flex flex-col bg-white overflow-x-auto">
      <div class="h-full flex flex-col min-w-[900px]">

        <!-- Column Headers -->
        <div class="bg-surface-100 border-b-2 border-black sticky top-0 z-5">
          <div class="grid grid-cols-[64px_180px_1fr_1fr_100px_100px_80px_120px] gap-2 text-black text-xs font-black uppercase tracking-wide px-3 py-2">
            <div class="text-center text-gray-500">ID</div>
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

        <!-- Rows -->
        <div class="flex-1 bg-white overflow-y-auto">
            <TraceInfiniteScroll initialPage={trace_page} filters={filters} height="800px">
              {#snippet children(trace: TraceListItem, index: number)}
                <div
                  class="grid grid-cols-[64px_180px_1fr_1fr_100px_100px_80px_120px] gap-2 items-center px-3 py-2.5 border-b border-gray-100 hover:bg-primary-100 cursor-pointer transition-colors {index % 2 === 0 ? 'bg-white' : 'bg-surface-500'}"
                  onclick={() => handleTraceClick(trace)}
                  onkeydown={(e) => e.key === 'Enter' && handleTraceClick(trace)}
                  role="button"
                  tabindex="0"
                >
                  <div class="text-center">
                    <span class="text-xs font-mono text-gray-400 bg-surface-200 px-1.5 py-0.5 rounded">{trace.trace_id.slice(0, 7)}</span>
                  </div>

                  <div class="flex items-center gap-2 min-w-0">
                    <div class={`w-1 h-5 rounded-sm flex-shrink-0 ${trace.has_errors ? 'bg-error-600' : 'bg-secondary-500'}`}></div>

                    <span class="text-xs text-black font-mono truncate">{formatTimestamp(trace.start_time)}</span>
                  </div>

                  <div class="flex items-center gap-2 min-w-0">
                    <span class="inline-block w-2 h-2 rounded-full bg-primary-500 flex-shrink-0"></span>
                    <span class="text-xs text-black truncate">{trace.service_name ?? 'Unknown'}</span>
                  </div>

                  <div class="min-w-0">
                    <span class="text-xs text-gray-700 truncate block">{trace.root_operation ?? 'N/A'}</span>
                  </div>

                  <div class="text-center">
                    <span class="text-xs text-black font-mono">{formatDuration(trace.duration_ms)}</span>
                  </div>

                  <div class="text-center">
                    <span class="px-2 py-0.5 rounded-base bg-surface-200 border border-black text-gray-800 text-xs font-bold">
                      {trace.scope ?? 'GET'}
                    </span>
                  </div>

                  <div class="text-center">
                    <span class="text-xs text-black font-mono font-bold">{trace.span_count ?? 0}</span>
                  </div>

                  <div class="text-center">
                    <span class={`inline-block px-2 py-0.5 rounded-base border border-black text-white text-xs font-black ${getStatusColor(trace.status_code)}`}>
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
</div>

{#if selectedTraceSpans && selectedTrace}
  <TraceDetailSidebar
    trace={selectedTrace}
    traceSpans={selectedTraceSpans}
    onClose={handleClosePanel}
  />
{/if}

{#if isLoadingDetail}
  <div class="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center">
    <div class="bg-white border-2 border-black rounded-base shadow p-6 flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-3 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-sm font-black text-primary-800 uppercase tracking-wide">Loading trace details</p>
    </div>
  </div>
{/if}