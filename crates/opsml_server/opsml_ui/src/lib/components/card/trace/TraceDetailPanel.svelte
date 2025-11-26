<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { TraceDetail, TraceSpan } from './types';
  import TraceWaterfall from './TraceWaterfall.svelte';
  import SpanDetailView from './SpanDetailView.svelte';
  import SpanGraph from './graph/SpanGraph.svelte';
  import { formatDuration } from './utils';
  import { Network, List } from 'lucide-svelte';

  let {
    traceDetail,
    onClose,
  }: {
    traceDetail: TraceDetail;
    onClose: () => void;
  } = $props();

  let selectedSpan = $state<TraceSpan | null>(traceDetail.root_span);
  let isClosing = $state(false);
  let showWaterfall = $state(true);
  let showSpanDetail = $state(true);
  let showGraph = $state(false);

  function handleClose() {
    isClosing = true;
    setTimeout(() => {
      onClose();
    }, 20);
  }

  const slowestSpan = $derived(() => {
    const childSpans = traceDetail.spans.filter(span => span.depth > 0);
    if (childSpans.length === 0) return null;

    return childSpans.reduce((max, span) =>
      (span.duration_ms || 0) > (max.duration_ms || 0) ? span : max
    );
  });

  function handleSpanSelect(span: TraceSpan) {
    selectedSpan = span;
    if (window.innerWidth < 1024) {
      showSpanDetail = true;
    }
  }

  function getStatusColor(hasError: boolean): string {
    return hasError ? 'bg-error-600' : 'bg-secondary-500';
  }

  function toggleWaterfall() {
    showWaterfall = !showWaterfall;
    if (!showWaterfall) showSpanDetail = true;
  }

  function toggleSpanDetail() {
    showSpanDetail = !showSpanDetail;
    if (!showSpanDetail) showWaterfall = true;
  }

  function toggleGraph() {
    showGraph = !showGraph;
  }

  onMount(() => {
    document.body.style.overflow = 'hidden';
  });

  onDestroy(() => {
    document.body.style.overflow = '';
  });
</script>

<!-- Backdrop -->
<div
  class="fixed inset-0 bg-opacity-30 z-40 transition-opacity duration-300"
  class:opacity-0={isClosing}
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="-1"
  aria-label="Close panel backdrop"
></div>

<!-- Side Panel -->
<div
  class="fixed top-0 right-0 h-full w-full lg:w-4/5 xl:w-3/4 bg-white border-l-4 border-black shadow-2xl z-50 overflow-hidden flex flex-col transition-transform duration-300"
  class:translate-x-full={isClosing}
>
  <!-- Header -->
  <div class="flex items-center justify-between p-4 border-b-2 border-black bg-surface-50">
    <div class="flex flex-col gap-2 flex-1 min-w-0">
      <div class="flex items-center gap-2">
        <div class={`w-2 h-10 rounded flex-shrink-0 ${getStatusColor(traceDetail.error_count > 0)}`}></div>
        <div class="min-w-0 flex-1">
          <h2 class="text-lg font-bold text-primary-800">Trace Details</h2>
          <p class="text-sm font-mono text-gray-600 truncate">{traceDetail.trace_id}</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">{traceDetail.span_count} spans</span>
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">{traceDetail.service_count} services</span>
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">{formatDuration(traceDetail.total_duration_ms)}</span>
        {#if traceDetail.error_count > 0}
          <span class="badge text-error-900 border-black border-1 shadow-small bg-error-100">{traceDetail.error_count} errors</span>
        {/if}
      </div>
    </div>

    <div class="flex gap-2 flex-shrink-0 ml-2">
      <!-- Graph Toggle Button -->
      <button
        onclick={toggleGraph}
        class="px-3 py-2 rounded-lg transition-colors border-2 border-black shadow-small flex items-center gap-2 {showGraph ? 'bg-primary-500 text-white' : 'bg-white text-primary-800 hover:bg-primary-100'}"
        aria-label="Toggle execution graph"
        title="Toggle execution graph"
      >
        <Network class="w-5 h-5" />
        <span class="hidden md:inline text-sm font-bold">Graph</span>
      </button>

      <!-- Close Button -->
      <button
        onclick={handleClose}
        class="p-2 bg-primary-800 text-white hover:bg-primary-500 rounded-lg transition-colors border-2 border-black shadow-small"
        aria-label="Close panel"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>

  <!-- Mobile View Tabs -->
  <div class="lg:hidden flex border-b-2 border-black bg-surface-200">
    <button
      onclick={toggleWaterfall}
      class="flex-1 py-2 text-sm font-bold transition-colors border-r-2 border-black {showWaterfall ? 'bg-primary-500 text-white' : 'bg-white text-primary-800'}"
    >
      <List class="w-4 h-4 inline-block mr-1" />
      Waterfall
    </button>
    <button
      onclick={toggleSpanDetail}
      class="flex-1 py-2 text-sm font-bold transition-colors {showSpanDetail ? 'bg-primary-500 text-white' : 'bg-white text-primary-800'}"
    >
      Span Details
    </button>
  </div>

  <!-- Execution Graph (Expandable) -->
  {#if showGraph}
    <div class="border-b-2 border-black bg-surface-50 p-4 overflow-auto" style="max-height: 50vh;">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-bold text-primary-800">Execution Flow</h3>
        <button
          onclick={toggleGraph}
          class="text-xs px-2 py-1 bg-surface-200 hover:bg-surface-300 rounded border-1 border-black text-gray-700"
        >
          Collapse
        </button>
      </div>
      <SpanGraph
        spans={traceDetail.spans}
        slowestSpan={slowestSpan()}
        onSpanSelect={handleSpanSelect}
      />
    </div>
  {/if}

  <!-- Main Content Area -->
  <div class="flex-1 overflow-hidden flex flex-col lg:flex-row">
    <!-- Waterfall View -->
    <div
      class="overflow-auto border-b-2 lg:border-b-0 lg:border-r-2 border-black min-h-0 lg:flex-1 {showWaterfall ? 'flex-1' : 'hidden'} lg:block"
    >
      <TraceWaterfall
        spans={traceDetail.spans}
        totalDuration={traceDetail.total_duration_ms}
        {selectedSpan}
        onSpanSelect={handleSpanSelect}
        slowestSpan={slowestSpan()}
      />
    </div>

    <!-- Span Detail View -->
    <div
      class="overflow-auto bg-surface-50 min-h-0 lg:flex-1 lg:w-2/5 {showSpanDetail ? 'flex-1' : 'hidden'} lg:block"
    >
      {#if selectedSpan}
        <SpanDetailView
          span={selectedSpan}
          onSpanSelect={handleSpanSelect}
          allSpans={traceDetail.spans}
          slowestSpan={slowestSpan()}
        />
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500 p-4 text-center">
          Select a span to view details
        </div>
      {/if}
    </div>
  </div>
</div>