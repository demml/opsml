<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { type Attribute,  type TraceListItem, type TraceSpan, type TraceSpansResponse } from './types';
  import { formatAttributeValue } from './types';
  import TraceWaterfall from './TraceWaterfall.svelte';
  import SpanDetailView from './SpanDetailView.svelte';
  import SpanGraph from './graph/SpanGraph.svelte';
  import { formatDuration } from './utils';
  import { Network, List } from 'lucide-svelte';
  import Pill from '../utils/Pill.svelte';
  import { Waypoints } from 'lucide-svelte';
  let {
    trace,
    traceSpans,
    onClose,
  }: {
    trace: TraceListItem;
    traceSpans: TraceSpansResponse;
    onClose: () => void;
  } = $props();

  let selectedSpan = $state<TraceSpan | null>(traceSpans.spans[0] || null);
  let spans = $state<TraceSpan[]>(traceSpans.spans);
  let traceAttributes = $state<Attribute[]>(trace.resource_attributes|| []);
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
    const childSpans = spans.filter(span => span.depth > 0);
    if (childSpans.length === 0) return null;

    return childSpans.reduce((max, span) =>
      (span.duration_ms || 0) > (max.duration_ms || 0) ? span : max
    );
  });

  const service_count = $derived(() => {
    const services = new Set<string>();
    spans.forEach(span => {
      if ( span.service_name) {
        services.add(span.service_name);
      }
    });
    return services.size;
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
  class="fixed top-0 right-0 h-full w-full lg:w-4/5 xl:w-3/4 bg-white border-l-4 border-black shadow-2xl z-50 flex flex-col transition-transform duration-300"
  class:translate-x-full={isClosing}
>
  <!-- Sticky Header -->
  <div class="flex items-start justify-between p-6 border-b-2 border-black bg-surface-50 gap-6 flex-shrink-0">
    <div class="flex flex-col gap-4 flex-1 min-w-0">
      <!-- Title & Trace ID -->
      <div class="flex items-center gap-3">
        <div class={`w-2 h-10 rounded flex-shrink-0 ${getStatusColor(trace.error_count > 0)}`}></div>
        <div class="min-w-0 flex-1">
          <h2 class="text-lg font-bold text-primary-800">Trace Details</h2>
          <p class="text-sm font-mono text-gray-600 truncate">{trace.trace_id}</p>
        </div>
      </div>

      <!-- Metrics Badges -->
      <div class="flex flex-wrap gap-1">
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          {trace.span_count} spans
        </span>
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          {service_count()} services
        </span>
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          {formatDuration(trace.duration_ms)}
        </span>
        {#if trace.error_count > 0}
          <span class="badge text-error-900 border-black border-1 shadow-small bg-error-100">
            {trace.error_count} errors
          </span>
        {/if}
      </div>

      <!-- Resource Attributes Section -->
      <div class="flex flex-wrap gap-1 text-xs"> 
        {#each traceAttributes as attr}
          <Pill key={attr.key} value={formatAttributeValue(attr.value)} textSize="text-xs" />
        {/each}
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-2 flex-shrink-0">
      <button
        onclick={toggleGraph}
        class="px-3 py-2 rounded-lg transition-colors border-2 border-black shadow-small flex items-center gap-2 {showGraph ? 'bg-primary-500 text-white' : 'bg-white text-primary-800 hover:bg-primary-100'}"
        aria-label="Toggle execution graph"
      >
        <Network class="w-5 h-5" />
        <span class="hidden md:inline text-sm font-bold">Graph</span>
      </button>

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

  <!-- Scrollable Content Area -->
  <div class="flex-1 overflow-y-auto min-h-0">
    <!-- Mobile Tabs -->
    <div class="lg:hidden flex border-b-2 border-black bg-surface-200 sticky top-0 z-10">
      <button
        onclick={toggleWaterfall}
        class="flex-1 py-3 text-sm font-bold transition-colors border-r-2 border-black {showWaterfall ? 'bg-primary-500 text-white' : 'bg-white text-primary-800'}"
      >
        <List class="w-4 h-4 inline-block mr-1" />
        Waterfall
      </button>
      <button
        onclick={toggleSpanDetail}
        class="flex-1 py-3 text-sm font-bold transition-colors {showSpanDetail ? 'bg-primary-500 text-white' : 'bg-white text-primary-800'}"
      >
        Span Details
      </button>
    </div>

    <!-- Execution Graph -->
    {#if showGraph}
      <div class="border-b-2 border-black bg-surface-50 p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-bold text-primary-800">Execution Flow</h3>
          <button
            onclick={toggleGraph}
            class="text-xs px-2 py-1 bg-surface-200 hover:bg-surface-300 rounded border-1 border-black text-gray-700"
          >
            Collapse
          </button>
        </div>
        <div class="border-2 border-black rounded bg-white">
          <SpanGraph spans={spans} slowestSpan={slowestSpan()} onSpanSelect={handleSpanSelect} />
        </div>
      </div>
    {/if}

    <!-- Waterfall + Span Details -->
    <div class="flex flex-col lg:flex-row min-h-[600px]">
      <div class="border-b-2 lg:border-b-0 lg:border-r-2 border-black lg:flex-1 {showWaterfall ? 'block' : 'hidden'} lg:block">
        <TraceWaterfall
          spans={spans}
          totalDuration={trace.duration_ms || 0}
          {selectedSpan}
          onSpanSelect={handleSpanSelect}
          slowestSpan={slowestSpan()}
        />
      </div>

      <div class="bg-surface-50 lg:flex-1 {showSpanDetail ? 'block' : 'hidden'} lg:block">
        {#if selectedSpan}
          <SpanDetailView span={selectedSpan} onSpanSelect={handleSpanSelect} allSpans={spans} slowestSpan={slowestSpan()} />
        {:else}
          <div class="flex items-center justify-center h-full text-gray-500 p-4 text-center">
            Select a span to view details
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>