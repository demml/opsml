<script lang="ts">
  import { type Attribute, type TraceListItem, type TraceSpan, type TraceSpansResponse } from './types';
  import { formatAttributeValue } from './types';
  import TraceWaterfall from './TraceWaterfall.svelte';
  import SpanDetailView from './SpanDetailView.svelte';
  import SpanGraph from './graph/SpanGraph.svelte';
  import { formatDuration } from './utils';
  import { Network, List, X, GitBranch, AlertTriangle, Clock, Layers, ChevronDown, ChevronUp } from 'lucide-svelte';
  import Pill from '../utils/Pill.svelte';

  let {
    trace,
    traceSpans,
    onClose,
    showCloseButton = true,
  }: {
    trace: TraceListItem;
    traceSpans: TraceSpansResponse;
    onClose?: () => void;
    showCloseButton?: boolean;
  } = $props();

  let selectedSpan = $state<TraceSpan | null>(traceSpans.spans[0] || null);
  let spans = $state<TraceSpan[]>(traceSpans.spans);
  let traceAttributes = $state<Attribute[]>(trace.resource_attributes || []);
  let showWaterfall = $state(true);
  let showSpanDetail = $state(true);
  let showGraph = $state(false);
  let showAttributes = $state(false);

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
      if (span.service_name) {
        services.add(span.service_name);
      }
    });
    return services.size;
  });

  const hasError = $derived(trace.error_count > 0);

  function handleSpanSelect(span: TraceSpan) {
    selectedSpan = span;
    if (window.innerWidth < 1024) {
      showSpanDetail = true;
    }
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
</script>

<div class="flex flex-col h-full overflow-hidden">

  <!-- Neo-Brutalist Header -->
  <header class="flex-shrink-0 border-b-2 border-black bg-surface-100">

    <!-- Top bar: title + actions -->
    <div class="flex items-center justify-between px-4 py-3 gap-4">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-3 h-3 rounded-full border-1 border-black flex-shrink-0 {hasError ? 'bg-error-600' : 'bg-secondary-500'}"></div>
        <div class="min-w-0">
          <h2 class="text-base font-black uppercase tracking-tight text-primary-800 leading-tight">Trace Details</h2>
          <p class="text-xs font-mono text-black/70 truncate">{trace.trace_id}</p>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-shrink-0">
        <button
          onclick={toggleGraph}
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold border-2 border-black rounded transition-all bg-primary-500 shadow-small shadow-hover-small"
          aria-label="Toggle execution graph"
        >
          <Network class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">Graph</span>
        </button>

        {#if showCloseButton && onClose}
          <button
            onclick={onClose}
            class="p-1.5 text-primary-800 bg-white rounded border-2 border-black shadow-small shadow-hover-small transition-all"
            aria-label="Close panel"
          >
            <X class="w-4 h-4" />
          </button>
        {/if}
      </div>
    </div>

    <!-- Stats strip -->
    <div class="px-4 pb-3 flex flex-wrap items-center gap-2">
      <div class="flex items-center gap-1.5 px-2.5 py-1 bg-primary-500 border border-black/30 text-xs font-bold text-white shadow-small">
        <Layers class="w-3.5 h-3.5" />
        {trace.span_count} spans
      </div>
      <div class="flex items-center gap-1.5 px-2.5 py-1 bg-primary-500 border border-black/30 text-xs font-bold text-white shadow-small">
        <GitBranch class="w-3.5 h-3.5" />
        {service_count()} services
      </div>
      <div class="flex items-center gap-1.5 px-2.5 py-1 bg-primary-500 border border-black/30 text-xs font-bold text-white shadow-small">
        <Clock class="w-3.5 h-3.5" />
        {formatDuration(trace.duration_ms)}
      </div>
      {#if hasError}
        <div class="flex items-center gap-1.5 px-2.5 py-1 bg-error-600 border border-black text-xs font-bold text-white shadow-small">
          <AlertTriangle class="w-3.5 h-3.5" />
          {trace.error_count} {trace.error_count === 1 ? 'error' : 'errors'}
        </div>
      {/if}

      {#if traceAttributes.length > 0}
        <button
          onclick={() => showAttributes = !showAttributes}
          class="flex items-center gap-1 px-2.5 py-1 bg-primary-500 hover:bg-white/40 border border-black/30 text-xs font-bold text-white shadow-small transition-colors hover:text-primary-800"
        >
          {traceAttributes.length} resource attrs
            {#if showAttributes}<ChevronUp class="w-3 h-3"/>{:else}<ChevronDown class="w-3 h-3"/>{/if}
        </button>
      {/if}
    </div>

    <!-- Collapsible resource attributes -->
    {#if showAttributes && traceAttributes.length > 0}
      <div class="px-4 pb-3 border-black/20 pt-2 flex flex-wrap gap-1">
        {#each traceAttributes as attr}
          <Pill key={attr.key} value={formatAttributeValue(attr.value)} textSize="text-xs" />
        {/each}
      </div>
    {/if}
  </header>

  <!-- Mobile Tabs -->
  <div class="lg:hidden flex border-b-2 border-black bg-surface-100 flex-shrink-0">
    <button
      onclick={toggleWaterfall}
      class="flex-1 py-2.5 text-xs font-black uppercase tracking-wide transition-colors border-r-2 border-black {showWaterfall ? 'bg-primary-500 text-black' : 'bg-white text-gray-700 hover:bg-surface-200'}"
    >
      <List class="w-3.5 h-3.5 inline-block mr-1" />
      Waterfall
    </button>
    <button
      onclick={toggleSpanDetail}
      class="flex-1 py-2.5 text-xs font-black uppercase tracking-wide transition-colors {showSpanDetail ? 'bg-primary-500 text-black' : 'bg-white text-gray-700 hover:bg-surface-200'}"
    >
      Span Detail
    </button>
  </div>

  <!-- Graph Panel -->
  {#if showGraph}
    <div class="border-b-2 border-black bg-surface-50 p-4 flex-shrink-0">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-xs font-black uppercase tracking-wide text-primary-800">Execution Flow</h3>
        <button
          onclick={toggleGraph}
          class="text-xs px-2 py-1 bg-primary-500 text-white font-bold rounded border-2 border-black hover:bg-primary-600 transition-colors shadow-small shadow-hover-small"
        >
          Collapse
        </button>
      </div>
      <div class="bg-white border-2 border-black rounded-base shadow-small">
        <SpanGraph spans={spans} slowestSpan={slowestSpan()} onSpanSelect={handleSpanSelect} />
      </div>
    </div>
  {/if}

  <!-- Main content: waterfall + span detail -->
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <div class="border-r-2 border-black flex-1 min-w-0 {showWaterfall ? 'flex' : 'hidden'} lg:flex flex-col">
      <TraceWaterfall
        spans={spans}
        totalDuration={trace.duration_ms || 0}
        {selectedSpan}
        onSpanSelect={handleSpanSelect}
        slowestSpan={slowestSpan()}
      />
    </div>

    <div class="flex-1 min-w-0 overflow-hidden {showSpanDetail ? 'flex' : 'hidden'} lg:flex flex-col bg-surface-50">
      {#if selectedSpan}
        <SpanDetailView span={selectedSpan} onSpanSelect={handleSpanSelect} allSpans={spans} slowestSpan={slowestSpan()} />
      {:else}
        <div class="flex flex-col items-center justify-center h-full gap-3 text-center p-8">
          <div class="w-12 h-12 rounded-full border-2 border-black bg-surface-200 flex items-center justify-center">
            <Layers class="w-6 h-6 text-gray-400" />
          </div>
          <p class="text-sm font-bold text-gray-500 uppercase tracking-wide">Select a span to inspect</p>
        </div>
      {/if}
    </div>
  </div>

</div>