<script lang="ts">
  /**
   * Integration mock: TraceDetailContent + GenAI tab.
   *
   * Layout:
   *   Fixed header (trace_id, chips) — identical chrome to TraceDetailContent
   *   Tab bar: Waterfall | Map | GenAI        ← GenAI is the new tab
   *   ┌─────────────────────────────────────┐
   *   │ Waterfall/Map → TraceWaterfall       │  (top, resizable)
   *   │ GenAI         → aggregate metrics    │
   *   ├─────────────────────────────────────┤  draggable divider
   *   │ Waterfall/Map → SpanDetailWithGenAi  │  (bottom)
   *   │ GenAI         → nothing extra        │
   *   └─────────────────────────────────────┘
   *
   * Span click in waterfall drives SpanDetailWithGenAi.
   * GenAiSpanRecord is looked up by span_id from genAiData.spans[].
   */
  import TraceWaterfall from '$lib/components/trace/TraceWaterfall.svelte';
  import SpanDetailWithGenAi from './SpanDetailWithGenAi.svelte';
  import type { TraceListItem, TraceSpan, TraceSpansResponse } from '$lib/components/trace/types';
  import type { GenAiSpanRecord, GenAiTraceMetricsResponse } from './types';
  import { formatDuration } from '$lib/components/trace/utils';
  import {
    Activity,
    AlertTriangle,
    BadgeCheck,
    Bot,
    ChevronLeft,
    ChevronUp,
    ChevronDown,
    Clock,
    Coins,
    Cpu,
    Database,
    Hash,
    Layers,
    List,
    MessageSquare,
    Network,
    Sparkles,
    Wrench
  } from 'lucide-svelte';
  import ChartCard from './ChartCard.svelte';
  import { buildOperationBarChart, buildSpanDurationBar } from './charts';
  import { fmtCompact, fmtInt, fmtMs, fmtUsd } from './format';

  let {
    genAiData,
    traceItem,
    traceSpans,
  }: {
    genAiData: GenAiTraceMetricsResponse;
    traceItem: TraceListItem;
    traceSpans: TraceSpansResponse;
  } = $props();

  // ── Tab state ─────────────────────────────────────────────────────────────
  type TopTab = 'waterfall' | 'map' | 'genai';
  let activeTopTab = $state<TopTab>('waterfall');

  // ── Resizable split (mirrors TraceDetailContent) ──────────────────────────
  let topPct = $state(50);
  let topCollapsed = $state(false);
  let isDragging = $state(false);
  let containerEl: HTMLDivElement;
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
    topPct = Math.min(90, Math.max(10, dragStartTopPct + deltaPct));
  }
  function onMouseUp() { isDragging = false; }

  // ── Span selection ────────────────────────────────────────────────────────
  let selectedSpan = $state<TraceSpan | null>(traceSpans.spans[0] || null);

  // Map span_id → GenAiSpanRecord for O(1) lookup
  const genAiSpanMap = $derived(
    new Map<string, GenAiSpanRecord>(genAiData.spans.map((s) => [s.span_id, s]))
  );

  const selectedGenAiSpan = $derived(
    selectedSpan ? (genAiSpanMap.get(selectedSpan.span_id) ?? null) : null
  );

  const slowestSpan = $derived((() => {
    const kids = traceSpans.spans.filter((s) => s.depth > 0);
    if (!kids.length) return null;
    return kids.reduce((m, s) => (s.duration_ms ?? 0) > (m.duration_ms ?? 0) ? s : m);
  })());

  function handleSpanSelect(span: TraceSpan) {
    selectedSpan = span;
  }

  // ── GenAI aggregate metrics ───────────────────────────────────────────────
  const summary = $derived(genAiData.agent_dashboard.summary);
  const traceCost = $derived(genAiData.agent_dashboard.buckets[0]?.total_cost ?? 0);
  const totalTokens = $derived(summary.total_input_tokens + summary.total_output_tokens);
  const errorCount = $derived(genAiData.spans.filter((s) => s.error_type).length);
  const evalCount = $derived(genAiData.spans.reduce((a, s) => a + s.eval_results.length, 0));
  const tokIn = $derived(summary.total_input_tokens);
  const tokOut = $derived(summary.total_output_tokens);
  const tokCC = $derived(summary.total_cache_creation_tokens);
  const tokCR = $derived(summary.total_cache_read_tokens);
  const tokSum = $derived(Math.max(1, tokIn + tokOut + tokCC + tokCR));
  const agentName = $derived(genAiData.spans.find((s) => s.agent_name)?.agent_name ?? null);
  const conversationId = $derived(genAiData.spans.find((s) => s.conversation_id)?.conversation_id ?? null);

  function headerTime(dt: string): string {
    try {
      return new Date(dt).toLocaleString('en-US', {
        month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true,
      });
    } catch { return dt; }
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

  <!-- ── Fixed header (same chrome as TraceDetailContent) ────────────────── -->
  <header class="flex-shrink-0 flex items-center justify-between px-4 py-2.5 border-b-2 border-black bg-primary-100 z-20 gap-4">
    <div class="flex items-center gap-2 min-w-0">
      <button class="flex items-center justify-center p-1.5 border-2 border-black bg-surface-50 shadow-small rounded-base text-primary-800">
        <ChevronLeft class="w-4 h-4" />
      </button>
      <nav class="flex items-center gap-1.5 text-xs font-mono min-w-0">
        <span class="text-primary-600 font-bold uppercase tracking-wide">Traces</span>
        <span class="text-primary-400">/</span>
        <span class="font-black text-primary-950 truncate max-w-[240px]" title={traceItem.trace_id}>
          {traceItem.trace_id}
        </span>
      </nav>
    </div>
    <div class="flex items-center gap-1.5 flex-shrink-0 flex-wrap justify-end">
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Clock class="w-3 h-3" /> {formatDuration(traceItem.duration_ms)}
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Layers class="w-3 h-3" /> {traceItem.span_count} spans
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-black rounded-base shadow-small font-mono">
        {traceItem.service_name}
      </span>
      {#if traceItem.error_count > 0}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-error-100 text-error-800 rounded-base shadow-small">
          <AlertTriangle class="w-3 h-3" /> {traceItem.error_count} {traceItem.error_count === 1 ? 'error' : 'errors'}
        </span>
      {/if}
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-700 rounded-base shadow-small font-mono">
        {headerTime(traceItem.start_time)}
      </span>
    </div>
  </header>

  <!-- ── Tab switcher: Waterfall | Map | GenAI ──────────────────────────── -->
  <div class="flex-shrink-0 flex items-center justify-between gap-2 px-4 py-2 border-b-2 border-black bg-surface-50 z-10">
    <div class="flex items-center gap-2">
      <div class="inline-flex border-2 border-black rounded-base overflow-hidden shadow-small">
        <button
          onclick={() => (activeTopTab = 'waterfall')}
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide transition-colors duration-100
            {activeTopTab === 'waterfall' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
        >
          <List class="w-3.5 h-3.5" /> Waterfall
        </button>
        <button
          onclick={() => (activeTopTab = 'map')}
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide border-l-2 border-black transition-colors duration-100
            {activeTopTab === 'map' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
        >
          <Network class="w-3.5 h-3.5" /> Map
        </button>
        {#if genAiData.has_genai_spans}
          <!-- ★ GenAI tab — only shown when trace has genai spans ★ -->
          <button
            onclick={() => (activeTopTab = 'genai')}
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide border-l-2 border-black transition-colors duration-100
              {activeTopTab === 'genai' ? 'bg-primary-500 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
          >
            <Sparkles class="w-3.5 h-3.5" /> GenAI
          </button>
        {/if}
      </div>

      <!-- Collapse toggle -->
      <button
        type="button"
        onclick={() => (topCollapsed = !topCollapsed)}
        class="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-black uppercase tracking-wide border-2 border-black bg-surface-50 text-primary-800 hover:bg-warning-200 rounded-base shadow-small transition-colors duration-100"
      >
        {#if topCollapsed}
          <ChevronDown class="w-3.5 h-3.5" /> Expand
        {:else}
          <ChevronUp class="w-3.5 h-3.5" /> Collapse
        {/if}
      </button>
    </div>

    <!-- GenAI context pills (always visible when genai data exists) -->
    {#if genAiData.has_genai_spans && agentName}
      <div class="flex items-center gap-1.5 text-[10px] font-mono text-gray-700">
        <Bot class="w-3 h-3" /> {agentName}
        {#if conversationId}
          <span>·</span>
          <MessageSquare class="w-3 h-3" />
          <span class="truncate max-w-[160px]">{conversationId}</span>
        {/if}
      </div>
    {/if}
  </div>

  <!-- ── Content ──────────────────────────────────────────────────────────── -->

  {#if activeTopTab === 'genai'}
    <!-- ── GenAI Tab: aggregate trace metrics from GenAiTraceMetricsResponse ── -->
    <div class="flex-1 min-h-0 overflow-auto">
      <div class="p-3 space-y-3">

        <!-- KPI rail -->
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {#each [
            { label: 'GenAI Spans', value: fmtInt(genAiData.spans.length), icon: Activity, accent: 'bg-surface-50' },
            { label: 'p50',         value: fmtMs(summary.p50_duration_ms), icon: Clock,         accent: 'bg-surface-50' },
            { label: 'p95',         value: fmtMs(summary.p95_duration_ms), icon: Clock,         accent: 'bg-surface-50' },
            { label: 'In / Out',    value: `${fmtCompact(tokIn)} / ${fmtCompact(tokOut)}`, icon: Cpu, accent: 'bg-surface-50' },
            { label: 'Cache',       value: `${fmtCompact(tokCC)} / ${fmtCompact(tokCR)}`, icon: Database, accent: 'bg-surface-50' },
            { label: 'Spend',       value: fmtUsd(traceCost),            icon: Coins,        accent: 'bg-warning-100' },
            { label: 'Errors',      value: fmtInt(errorCount),           icon: AlertTriangle,accent: errorCount > 0 ? 'bg-error-100' : 'bg-surface-50' },
            { label: 'Evals',       value: fmtInt(evalCount),            icon: BadgeCheck,   accent: 'bg-success-100' },
          ] as kpi}
            <div class="rounded-base border-2 border-black shadow-small {kpi.accent} px-2 py-1.5">
              <div class="flex items-center gap-1 text-[9px] font-black text-primary-700 uppercase tracking-widest">
                <kpi.icon class="w-2.5 h-2.5" /> {kpi.label}
              </div>
              <div class="text-sm font-black text-black leading-tight truncate">{kpi.value}</div>
            </div>
          {/each}
        </div>

        <!-- Token mix bar -->
        <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
          <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center justify-between">
            <span class="text-[11px] font-black uppercase tracking-wide text-primary-800">Token Mix</span>
            <span class="text-[10px] font-mono text-gray-700">{fmtCompact(tokSum)} total</span>
          </div>
          <div class="p-2 space-y-1.5">
            <div class="flex w-full h-4 border-2 border-black rounded-base overflow-hidden">
              <div class="bg-primary-500"  style="width: {(tokIn  / tokSum) * 100}%"></div>
              <div class="bg-success-400"  style="width: {(tokOut / tokSum) * 100}%"></div>
              <div class="bg-tertiary-400" style="width: {(tokCC  / tokSum) * 100}%"></div>
              <div class="bg-warning-400"  style="width: {(tokCR  / tokSum) * 100}%"></div>
            </div>
            <div class="flex flex-wrap gap-3 text-[10px] font-mono">
              <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-primary-500  border border-black"></span>input {fmtCompact(tokIn)} ({((tokIn/tokSum)*100).toFixed(1)}%)</span>
              <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-success-400  border border-black"></span>output {fmtCompact(tokOut)} ({((tokOut/tokSum)*100).toFixed(1)}%)</span>
              <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-tertiary-400 border border-black"></span>cache_create {fmtCompact(tokCC)}</span>
              <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-warning-400  border border-black"></span>cache_read {fmtCompact(tokCR)}</span>
            </div>
          </div>
        </div>

        <!-- 2-up charts -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <ChartCard
            title="Operations"
            subtitle="span count"
            height="h-36"
            configFn={() => buildOperationBarChart(genAiData.operation_breakdown.operations)}
          />
          <ChartCard
            title="Span Duration"
            subtitle="slowest first"
            height="h-36"
            configFn={() => buildSpanDurationBar(genAiData.spans)}
          />
        </div>

        <!-- 3-column tables: Models / Tools / Errors -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <!-- Models -->
          <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
            <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
              <Cpu class="w-3 h-3 text-primary-700" />
              <span class="text-[11px] font-black uppercase text-primary-800">Models</span>
            </div>
            <table class="w-full text-xs">
              <thead class="bg-surface-100 border-b-2 border-black">
                <tr>
                  <th class="px-2 py-1 text-left font-black text-primary-700 uppercase text-[9px]">Model</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">Spans</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">In/Out tok</th>
                </tr>
              </thead>
              <tbody>
                {#each genAiData.model_usage.models as m}
                  <tr class="border-b border-gray-200 hover:bg-primary-50">
                    <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[120px]">{m.model}</td>
                    <td class="px-2 py-1 text-right font-mono">{fmtInt(m.span_count)}</td>
                    <td class="px-2 py-1 text-right font-mono">{fmtCompact(m.total_input_tokens)}/{fmtCompact(m.total_output_tokens)}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>

          <!-- Tools -->
          <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
            <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
              <Wrench class="w-3 h-3 text-primary-700" />
              <span class="text-[11px] font-black uppercase text-primary-800">Tools</span>
            </div>
            <table class="w-full text-xs">
              <thead class="bg-surface-100 border-b-2 border-black">
                <tr>
                  <th class="px-2 py-1 text-left font-black text-primary-700 uppercase text-[9px]">Tool</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">Calls</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">Avg ms</th>
                </tr>
              </thead>
              <tbody>
                {#each genAiData.tool_dashboard.aggregates as t}
                  <tr class="border-b border-gray-200 hover:bg-primary-50">
                    <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate">{t.tool_name ?? '—'}</td>
                    <td class="px-2 py-1 text-right font-mono">{fmtInt(t.call_count)}</td>
                    <td class="px-2 py-1 text-right font-mono">{fmtMs(t.avg_duration_ms)}</td>
                  </tr>
                {/each}
                {#if genAiData.tool_dashboard.aggregates.length === 0}
                  <tr><td colspan="3" class="px-2 py-2 text-center text-gray-500 italic">no tool calls</td></tr>
                {/if}
              </tbody>
            </table>
          </div>

          <!-- Errors -->
          <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
            <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
              <AlertTriangle class="w-3 h-3 text-error-700" />
              <span class="text-[11px] font-black uppercase text-primary-800">Errors</span>
            </div>
            <div class="divide-y divide-gray-200">
              {#each genAiData.error_breakdown.errors as e}
                {@const max = Math.max(...genAiData.error_breakdown.errors.map((x) => x.count))}
                <div class="px-2 py-1.5 flex items-center gap-2 text-[11px]">
                  <span class="font-mono font-bold text-primary-900 truncate flex-1">{e.error_type}</span>
                  <div class="w-20 h-2.5 bg-surface-100 border border-black rounded-base overflow-hidden">
                    <div class="h-full bg-error-300" style="width: {(e.count / max) * 100}%"></div>
                  </div>
                  <span class="font-mono text-error-700 font-bold w-6 text-right">{fmtInt(e.count)}</span>
                </div>
              {/each}
              {#if genAiData.error_breakdown.errors.length === 0}
                <div class="px-2 py-3 text-center text-gray-500 italic text-xs">no errors in trace</div>
              {/if}
            </div>
          </div>
        </div>

        <!-- Agent activity -->
        {#if genAiData.agent_activity.agents.length > 0}
          <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
            <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
              <Bot class="w-3 h-3 text-primary-700" />
              <span class="text-[11px] font-black uppercase text-primary-800">Agent Activity</span>
            </div>
            <table class="w-full text-xs">
              <thead class="bg-surface-100 border-b-2 border-black">
                <tr>
                  <th class="px-2 py-1 text-left font-black text-primary-700 uppercase text-[9px]">Agent</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">Spans</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">In tok</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">Out tok</th>
                  <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-[9px]">Conversation</th>
                </tr>
              </thead>
              <tbody>
                {#each genAiData.agent_activity.agents as a}
                  <tr class="border-b border-gray-200 hover:bg-primary-50">
                    <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate">{a.agent_name ?? '—'}</td>
                    <td class="px-2 py-1 text-right font-mono">{fmtInt(a.span_count)}</td>
                    <td class="px-2 py-1 text-right font-mono">{fmtCompact(a.total_input_tokens)}</td>
                    <td class="px-2 py-1 text-right font-mono">{fmtCompact(a.total_output_tokens)}</td>
                    <td class="px-2 py-1 text-right font-mono text-gray-700 truncate max-w-[120px]">{a.conversation_id ?? '—'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}

      </div>
    </div>

  {:else}
    <!-- ── Waterfall / Map tabs: resizable split ───────────────────────────── -->
    <div class="flex flex-col flex-1 min-h-0 overflow-hidden">

      <!-- Top: Waterfall -->
      <div
        class="flex-shrink-0 overflow-hidden transition-[height] duration-200 ease-out"
        style="height: {topCollapsed ? 0 : topPct}%;"
      >
        {#if activeTopTab === 'waterfall'}
          <div class="h-full">
            <TraceWaterfall
              spans={traceSpans.spans}
              totalDuration={traceItem.duration_ms ?? 0}
              {selectedSpan}
              onSpanSelect={handleSpanSelect}
              slowestSpan={slowestSpan}
            />
          </div>
        {:else}
          <div class="h-full flex items-center justify-center bg-surface-50 border-b-2 border-black text-primary-400 text-sm font-bold uppercase">
            Map view — unchanged from existing SpanGraph
          </div>
        {/if}
      </div>

      <!-- Draggable divider -->
      {#if !topCollapsed}
        <button
          type="button"
          class="flex-shrink-0 relative flex items-center justify-center border-t-2 border-b-2 border-black bg-primary-100 cursor-row-resize z-10 select-none w-full hover:bg-primary-200 transition-colors duration-100"
          style="height: 14px;"
          onmousedown={onDividerMouseDown}
          aria-label="Resize panels"
          tabindex="0"
        >
          <div class="flex items-center gap-0.5 pointer-events-none">
            {#each [0,1,2,3,4] as dot (dot)}
              <div class="w-4 h-0.5 rounded-full bg-primary-700/40"></div>
            {/each}
          </div>
        </button>
      {/if}

      <!-- Bottom: Span detail with optional GenAI tab -->
      <div class="flex-1 min-h-0 overflow-hidden">
        {#if selectedSpan}
          <SpanDetailWithGenAi
            span={selectedSpan}
            genAiSpan={selectedGenAiSpan}
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
  {/if}

</div>
