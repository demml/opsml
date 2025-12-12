<script lang="ts">
  import MultiComboBoxDropDown from '$lib/components/utils/MultiComboBoxDropDown.svelte';
  import type { TraceListItem, TracePaginationResponse, TraceSpansResponse, } from './types';
  import TraceDetailPanel from './TraceDetailPanel.svelte';
  import TraceInfiniteScroll from './TraceInfiniteScroll.svelte';
  import { getServerTraceSpans } from './utils';
  import type { TracePageFilter } from './types';
  import MultiComboSearchBox from '../utils/MultiComboSearchBox.svelte';

  let { trace_page, filters } = $props<{ trace_page: TracePaginationResponse, filters: TracePageFilter }>();
  let filteredTags: string[] = $state([]);
  let availableTags: string[] = $state([]);

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

</script>

<div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
  <!-- Filter sidebar -->
  <div class="col-span-1 lg:col-span-1 p-2 flex flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 self-start overflow-hidden">
    <MultiComboBoxDropDown
      boxId="tag-search-input"
      label="Search Tags"
      bind:filteredItems={filteredTags}
      availableOptions={availableTags}
    />

    <MultiComboSearchBox
      boxId="tag-search-input"
      label="Search Tags"
      bind:filteredItems={filteredTags}
    />

  </div>

  <div class="col-span-1 lg:col-span-4 gap-1 py-2 px-4 flex-1 flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50">
    <div class="flex flex-col h-full">
      <div class="items-center mr-2 font-bold text-primary-800 text-lg mb-2">Traces</div>

      <div class="flex-1 overflow-x-auto border-2 border-black rounded-lg">
        <div class="h-full flex flex-col min-w-[900px]">

          <div class="bg-white border-b-2 border-black sticky top-0 z-10">
            <div class="grid grid-cols-[64px_180px_1fr_1fr_100px_100px_80px_120px] gap-2 text-black text-sm font-heading px-2 py-2">
              <div class="text-center">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Id</span>
              </div>
              <div class="text-left">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Date</span>
              </div>
              <div class="text-left">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Service</span>
              </div>
              <div class="text-left">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Resource</span>
              </div>
              <div class="text-center">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Duration</span>
              </div>
              <div class="text-center">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Method</span>
              </div>
              <div class="text-center">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Spans</span>
              </div>
              <div class="text-center">
                <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Status</span>
              </div>
            </div>
          </div>

          <div class="flex-1 bg-white overflow-y-auto">
            <TraceInfiniteScroll initialPage={trace_page} filters={filters} height="800px">
              {#snippet children(trace: TraceListItem, index: number)}
                <div
                  class="grid grid-cols-[64px_180px_1fr_1fr_100px_100px_80px_120px] gap-2 items-center px-2 py-2 border-b border-gray-200 hover:bg-primary-200 cursor-pointer transition-colors {index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}"
                  onclick={() => handleTraceClick(trace)}
                  onkeydown={(e) => e.key === 'Enter' && handleTraceClick(trace)}
                  role="button"
                  tabindex="0"
                >
                  <div class="text-center">
                    <span class="text-xs font-mono text-gray-500">{trace.trace_id.slice(0, 7)}</span>
                  </div>

                  <div class="flex items-center gap-2 min-w-0">
                    <div class={`w-1.5 h-4 rounded-sm flex-shrink-0 ${trace.has_errors ? 'bg-error-600' : 'bg-secondary-500'}`}></div>
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
                    <span class="px-2 py-1 rounded bg-gray-100 text-gray-800 text-xs font-medium">
                      {trace.scope ?? 'GET'}
                    </span>
                  </div>

                  <div class="text-center">
                    <span class="text-xs text-black font-medium">{trace.span_count ?? 0}</span>
                  </div>

                  <div class="text-center">
                    <span class={`inline-block px-2 py-1 rounded text-white text-xs font-bold ${getStatusColor(trace.status_code)}`}>
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
</div>

{#if selectedTraceSpans && selectedTrace}
  <TraceDetailPanel
    trace={selectedTrace}
    traceSpans={selectedTraceSpans}
    onClose={handleClosePanel}
  />
{/if}

{#if isLoadingDetail}
  <div class="fixed inset-0 bg-opacity-30 z-50 flex items-center justify-center">
    <div class="bg-white border-4 border-black rounded-lg p-8 shadow-2xl">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
      <p class="mt-4 text-sm font-bold text-primary-800">Loading trace details...</p>
    </div>
  </div>
{/if}