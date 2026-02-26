<script lang="ts">
  import { type TraceListItem, type TraceSpansResponse, type TraceSpan } from './types';
  import TraceWaterfall from './TraceWaterfall.svelte';
  import SpanDetailView from './SpanDetailView.svelte';
  import SpanGraph from './graph/SpanGraph.svelte';
  import { formatDuration } from './utils';
  import { Network, List, X, ChevronLeft, Clock, Layers, AlertTriangle, PanelRightClose } from 'lucide-svelte';

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
  let activeTopTab = $state<'waterfall' | 'map'>('waterfall');
  let spanPanelOpen = $state(true);

  const slowestSpan = $derived(() => {
    const childSpans = spans.filter(span => span.depth > 0);
    if (childSpans.length === 0) return null;
    return childSpans.reduce((max, span) =>
      (span.duration_ms || 0) > (max.duration_ms || 0) ? span : max
    );
  });

  const hasError = $derived(trace.error_count > 0);

  function formatHeaderTime(dt: string): string {
    try {
      return new Date(dt).toLocaleString('en-US', {
        month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true,
      });
    } catch {
      return dt;
    }
  }

  function handleSpanSelect(span: TraceSpan) {
    selectedSpan = span;
    spanPanelOpen = true;
  }

  function closeSpanPanel() {
    spanPanelOpen = false;
    selectedSpan = null;
  }
</script>

<div class="flex flex-col h-full overflow-hidden bg-surface-50">

  <!-- ─── Fixed header ────────────────────────────────────────────────────── -->
  <header class="flex-shrink-0 flex items-center justify-between px-4 py-2.5 border-b-2 border-black bg-surface-50 shadow-small z-20 gap-4">

    <!-- Left: back nav + breadcrumb -->
    <div class="flex items-center gap-2 min-w-0">
      {#if showCloseButton && onClose}
        <button
          onclick={onClose}
          class="flex items-center justify-center p-1.5 border-2 border-black bg-surface-50 shadow-small shadow-hover-small rounded-base transition-all text-primary-800"
          aria-label="Back to traces"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
      {/if}
      <nav class="flex items-center gap-1.5 text-xs font-mono min-w-0" aria-label="breadcrumb">
        <span class="text-primary-700 font-bold">Traces</span>
        <span class="text-primary-400">/</span>
        <span
          class="font-black text-primary-800 truncate max-w-[200px] sm:max-w-xs"
          title={trace.trace_id}
        >{trace.trace_id}</span>
      </nav>
    </div>

    <!-- Right: metadata chips + close -->
    <div class="flex items-center gap-1.5 flex-shrink-0 flex-wrap justify-end">
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-primary-100 text-primary-800 rounded-base shadow-small">
        <Clock class="w-3 h-3" />
        {formatDuration(trace.duration_ms)}
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-primary-100 text-primary-800 rounded-base shadow-small">
        <Layers class="w-3 h-3" />
        {trace.span_count} spans
      </span>
      {#if trace.service_name}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-200 text-black rounded-base shadow-small font-mono truncate max-w-[140px]">
          {trace.service_name}
        </span>
      {/if}
      {#if hasError}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-error-100 text-error-800 rounded-base shadow-small">
          <AlertTriangle class="w-3 h-3" />
          {trace.error_count} {trace.error_count === 1 ? 'error' : 'errors'}
        </span>
      {/if}
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-200 text-primary-800 rounded-base shadow-small font-mono">
        {formatHeaderTime(trace.start_time)}
      </span>

      {#if showCloseButton && onClose}
        <button
          onclick={onClose}
          class="p-1.5 border-2 border-black bg-surface-50 shadow-small shadow-hover-small rounded-base text-primary-800 transition-all"
          aria-label="Close"
        >
          <X class="w-4 h-4" />
        </button>
      {/if}
    </div>
  </header>

  <!-- ─── Top-tab switcher (Waterfall / Map) ──────────────────────────────── -->
  <div class="flex-shrink-0 flex items-center gap-1 px-4 py-2 border-b-2 border-black bg-surface-50 z-10">
    <div class="inline-flex border-2 border-black rounded-base overflow-hidden shadow-small">
      <button
        onclick={() => activeTopTab = 'waterfall'}
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide transition-colors duration-100 ease-out
          {activeTopTab === 'waterfall' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-surface-200'}"
      >
        <List class="w-3.5 h-3.5" />
        Waterfall
      </button>
      <button
        onclick={() => activeTopTab = 'map'}
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide border-l-2 border-black transition-colors duration-100 ease-out
          {activeTopTab === 'map' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-surface-200'}"
      >
        <Network class="w-3.5 h-3.5" />
        Map
      </button>
    </div>

    <!-- Span panel toggle (when a span is selected) -->
    {#if selectedSpan}
      <button
        onclick={() => spanPanelOpen = !spanPanelOpen}
        class="ml-auto flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide border-2 border-black rounded-base shadow-small shadow-hover-small transition-all duration-100
          {spanPanelOpen ? 'bg-primary-100 text-primary-800' : 'bg-surface-50 text-primary-800'}"
        aria-label="Toggle span detail"
      >
        <PanelRightClose class="w-3.5 h-3.5" />
        {spanPanelOpen ? 'Hide' : 'Span Detail'}
      </button>
    {/if}
  </div>

  <!-- ─── Main area: waterfall + span detail side-by-side ─────────────────── -->
  <div class="flex flex-1 min-h-0 overflow-hidden">

    <!-- Left: Waterfall or Map -->
    <div class="flex-1 min-w-0 overflow-hidden border-r-2 {spanPanelOpen && selectedSpan ? 'border-black' : 'border-transparent'}">
      {#if activeTopTab === 'waterfall'}
        <div class="h-full">
          <TraceWaterfall
            spans={spans}
            totalDuration={trace.duration_ms || 0}
            {selectedSpan}
            onSpanSelect={handleSpanSelect}
            slowestSpan={slowestSpan()}
          />
        </div>
      {:else}
        <div class="h-full bg-surface-50 p-3 overflow-auto">
          <div class="bg-surface-50 border-2 border-black rounded-base shadow-small h-full overflow-hidden">
            <SpanGraph spans={spans} slowestSpan={slowestSpan()} onSpanSelect={handleSpanSelect} />
          </div>
        </div>
      {/if}
    </div>

    <!-- Right: Span detail panel (slides in) -->
    {#if selectedSpan && spanPanelOpen}
      <div
        class="flex-shrink-0 flex flex-col overflow-hidden bg-surface-50 border-l-0 transition-all duration-200 ease-out"
        style="width: 42%;"
      >
        <!-- Span panel header -->
        <div class="flex-shrink-0 flex items-center justify-between px-3 py-2 border-b-2 border-black bg-primary-100">
          <span class="text-xs font-black uppercase tracking-wide text-primary-900">Span Detail</span>
          <button
            onclick={closeSpanPanel}
            class="p-1 border-2 border-black bg-surface-50 shadow-small shadow-click-small rounded-base text-primary-800 transition-all"
            aria-label="Close span detail"
          >
            <X class="w-3.5 h-3.5" />
          </button>
        </div>
        <div class="flex-1 min-h-0 overflow-hidden">
          <SpanDetailView
            span={selectedSpan}
            onSpanSelect={handleSpanSelect}
            allSpans={spans}
            slowestSpan={slowestSpan()}
            resourceAttributes={trace.resource_attributes}
          />
        </div>
      </div>
    {:else if !selectedSpan}
      <!-- No span selected placeholder (only shown if panel area is still laid out) -->
    {/if}

  </div>

</div>
