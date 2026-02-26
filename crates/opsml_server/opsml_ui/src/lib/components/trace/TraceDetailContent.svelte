<script lang="ts">
  import { type TraceListItem, type TraceSpansResponse, type TraceSpan } from './types';
  import TraceWaterfall from './TraceWaterfall.svelte';
  import SpanDetailView from './SpanDetailView.svelte';
  import SpanGraph from './graph/SpanGraph.svelte';
  import { formatDuration } from './utils';
  import { Network, List, X, ChevronLeft, Clock, Layers, AlertTriangle } from 'lucide-svelte';

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

  // Draggable divider — topPct is % height for the top (waterfall) panel
  let topPct = $state(52);
  let isDragging = $state(false);
  let containerEl: HTMLDivElement;

  const slowestSpan = $derived(() => {
    const childSpans = spans.filter(s => s.depth > 0);
    if (childSpans.length === 0) return null;
    return childSpans.reduce((max, s) =>
      (s.duration_ms || 0) > (max.duration_ms || 0) ? s : max
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
  }

  // ─── Drag-to-resize ──────────────────────────────────────────────────────

  let dragStartY = 0;
  let dragStartTopPct = 0;

  function onDividerMouseDown(e: MouseEvent) {
    isDragging = true;
    dragStartY = e.clientY;
    dragStartTopPct = topPct;
    e.preventDefault();
  }

  function onMouseMove(e: MouseEvent) {
    if (!isDragging || !containerEl) return;
    const rect = containerEl.getBoundingClientRect();
    const deltaPct = ((e.clientY - dragStartY) / rect.height) * 100;
    topPct = Math.min(75, Math.max(25, dragStartTopPct + deltaPct));
  }

  function onMouseUp() {
    isDragging = false;
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="flex flex-col h-full overflow-hidden bg-surface-50"
  bind:this={containerEl}
  onmousemove={onMouseMove}
  onmouseup={onMouseUp}
  onmouseleave={onMouseUp}
>

  <!-- ─── Fixed header ────────────────────────────────────────────────────── -->
  <header class="flex-shrink-0 flex items-center justify-between px-4 py-2.5 border-b-2 border-black bg-primary-100 z-20 gap-4">

    <!-- Left: back nav + breadcrumb -->
    <div class="flex items-center gap-2 min-w-0">
      {#if showCloseButton && onClose}
        <button
          onclick={onClose}
          class="flex items-center justify-center p-1.5 border-2 border-black bg-surface-50 shadow-small shadow-hover-small rounded-base transition-all duration-100 text-primary-800"
          aria-label="Back to traces"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
      {/if}
      <nav class="flex items-center gap-1.5 text-xs font-mono min-w-0" aria-label="breadcrumb">
        <span class="text-primary-600 font-bold uppercase tracking-wide">Traces</span>
        <span class="text-primary-400">/</span>
        <span
          class="font-black text-primary-950 truncate max-w-[240px] sm:max-w-sm"
          title={trace.trace_id}
        >{trace.trace_id}</span>
      </nav>
    </div>

    <!-- Right: metadata chips + close -->
    <div class="flex items-center gap-1.5 flex-shrink-0 flex-wrap justify-end">
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Clock class="w-3 h-3" />
        {formatDuration(trace.duration_ms)}
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Layers class="w-3 h-3" />
        {trace.span_count} spans
      </span>
      {#if trace.service_name}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-black rounded-base shadow-small font-mono truncate max-w-[140px]">
          {trace.service_name}
        </span>
      {/if}
      {#if hasError}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-error-100 text-error-800 rounded-base shadow-small">
          <AlertTriangle class="w-3 h-3" />
          {trace.error_count} {trace.error_count === 1 ? 'error' : 'errors'}
        </span>
      {/if}
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-700 rounded-base shadow-small font-mono">
        {formatHeaderTime(trace.start_time)}
      </span>

      {#if showCloseButton && onClose}
        <button
          onclick={onClose}
          class="p-1.5 border-2 border-black bg-primary-800 text-white hover:bg-primary-500 shadow-small shadow-click-small rounded-base transition-all duration-100"
          aria-label="Close"
        >
          <X class="w-4 h-4" />
        </button>
      {/if}
    </div>
  </header>

  <!-- ─── Tab switcher (Waterfall / Map) ──────────────────────────────────── -->
  <div class="flex-shrink-0 flex items-center gap-0 px-4 py-2 border-b-2 border-black bg-surface-50 z-10">
    <div class="inline-flex border-2 border-black rounded-base overflow-hidden shadow-small">
      <button
        onclick={() => activeTopTab = 'waterfall'}
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide transition-colors duration-100 ease-out
          {activeTopTab === 'waterfall' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
      >
        <List class="w-3.5 h-3.5" />
        Waterfall
      </button>
      <button
        onclick={() => activeTopTab = 'map'}
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide border-l-2 border-black transition-colors duration-100 ease-out
          {activeTopTab === 'map' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
      >
        <Network class="w-3.5 h-3.5" />
        Map
      </button>
    </div>
  </div>

  <!-- ─── Resizable vertical split ────────────────────────────────────────── -->
  <div class="flex flex-col flex-1 min-h-0 overflow-hidden">

    <!-- Top panel: Waterfall or Map -->
    <div
      class="flex-shrink-0 overflow-hidden"
      style="height: {topPct}%;"
    >
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
          <div class="bg-surface-50 p-8overflow-y-scroll">
            <SpanGraph spans={spans} slowestSpan={slowestSpan()} onSpanSelect={handleSpanSelect} />
          </div>
        </div>
      {/if}
    </div>

    <!-- Draggable divider -->
    <button
      type="button"
      class="flex-shrink-0 relative flex items-center justify-center border-t-2 border-b-2 border-black bg-primary-100 cursor-row-resize z-10 select-none w-full hover:bg-primary-200 transition-colors duration-100"
      style="height: 14px;"
      onmousedown={onDividerMouseDown}
      aria-label="Resize panels"
      tabindex="0"
    >
      <div class="flex items-center gap-0.5 pointer-events-none">
        {#each [0,1,2,3,4] as _}
          <div class="w-4 h-0.5 rounded-full bg-primary-700/40"></div>
        {/each}
      </div>
    </button>

    <!-- Bottom panel: Span detail -->
    <div class="flex-1 min-h-0 overflow-hidden border-t-0">
      {#if selectedSpan}
        <SpanDetailView
          span={selectedSpan}
          onSpanSelect={handleSpanSelect}
          allSpans={spans}
          slowestSpan={slowestSpan()}
          resourceAttributes={trace.resource_attributes}
        />
      {:else}
        <div class="flex flex-col items-center justify-center h-full gap-3 text-center p-8">
          <div class="w-12 h-12 border-2 border-black bg-surface-200 flex items-center justify-center rounded-base shadow-small">
            <Layers class="w-6 h-6 text-primary-400" />
          </div>
          <p class="text-sm font-black text-primary-500 uppercase tracking-wide">Select a span to inspect</p>
        </div>
      {/if}
    </div>

  </div>

</div>
