<script lang="ts">
  import {
    Activity,
    AlertTriangle,
    BadgeCheck,
    Bot,
    Boxes,
    Clock,
    Coins,
    Cpu,
    Hash,
    Wrench
  } from 'lucide-svelte';
  import { fmtCompact, fmtInt, fmtMs, fmtUsd } from './format';
  import type { GenAiSpanRecord, GenAiTraceMetricsResponse } from './types';

  let { data }: { data: GenAiTraceMetricsResponse } = $props();

  const summary = $derived(data.agent_dashboard.summary);
  const traceCost = $derived(data.agent_dashboard.buckets[0]?.total_cost ?? 0);
  const totalTokens = $derived(
    summary.total_input_tokens + summary.total_output_tokens
  );

  const traceStartMs = $derived(
    Math.min(...data.spans.map((s) => new Date(s.start_time).getTime()))
  );
  const traceEndMs = $derived(
    Math.max(
      ...data.spans.map((s) =>
        s.end_time ? new Date(s.end_time).getTime() : new Date(s.start_time).getTime() + s.duration_ms
      )
    )
  );
  const totalDurationMs = $derived(Math.max(1, traceEndMs - traceStartMs));

  // Build depth map by walking parent chain
  const depthMap = $derived(
    (() => {
      const byId = new Map(data.spans.map((s) => [s.span_id, s]));
      const cache = new Map<string, number>();
      function depthOf(s: GenAiSpanRecord): number {
        if (cache.has(s.span_id)) return cache.get(s.span_id)!;
        if (!s.parent_span_id) {
          cache.set(s.span_id, 0);
          return 0;
        }
        const parent = byId.get(s.parent_span_id);
        const d = parent ? depthOf(parent) + 1 : 0;
        cache.set(s.span_id, d);
        return d;
      }
      data.spans.forEach(depthOf);
      return cache;
    })()
  );

  // Sort spans hierarchically: root first, then children, depth-first
  const orderedSpans = $derived(
    (() => {
      const byParent = new Map<string | null, GenAiSpanRecord[]>();
      for (const s of data.spans) {
        const k = s.parent_span_id;
        if (!byParent.has(k)) byParent.set(k, []);
        byParent.get(k)!.push(s);
      }
      const out: GenAiSpanRecord[] = [];
      function walk(parentId: string | null) {
        const kids = (byParent.get(parentId) ?? []).sort(
          (a, b) =>
            new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
        );
        for (const k of kids) {
          out.push(k);
          walk(k.span_id);
        }
      }
      walk(null);
      return out;
    })()
  );

  let selectedSpanId = $state<string>(
    (data.spans.find((s) => s.input_messages) ?? data.spans[0])?.span_id ?? ''
  );
  const selectedSpan = $derived(
    data.spans.find((s) => s.span_id === selectedSpanId) ?? data.spans[0]
  );

  function pretty(s: string | null): string {
    if (!s) return '—';
    try {
      return JSON.stringify(JSON.parse(s), null, 2);
    } catch {
      return s;
    }
  }

  function spanIconFor(s: GenAiSpanRecord) {
    if (s.tool_name) return Wrench;
    if (s.operation_name === 'invoke_agent') return Bot;
    if (s.operation_name === 'embeddings') return Boxes;
    if (s.provider_name) return Cpu;
    return Activity;
  }

  function barColor(s: GenAiSpanRecord): string {
    if (s.error_type) return 'bg-error-400 border-error-700';
    if (s.tool_name) return 'bg-warning-400 border-warning-700';
    if (s.operation_name === 'invoke_agent') return 'bg-primary-500 border-primary-800';
    if (s.provider_name === 'openai') return 'bg-success-400 border-primary-800';
    if (s.provider_name === 'anthropic') return 'bg-tertiary-400 border-primary-800';
    return 'bg-surface-300 border-black';
  }

  function offsetPct(s: GenAiSpanRecord): number {
    return ((new Date(s.start_time).getTime() - traceStartMs) / totalDurationMs) * 100;
  }
  function widthPct(s: GenAiSpanRecord): number {
    return Math.max(0.5, (s.duration_ms / totalDurationMs) * 100);
  }
</script>

<div class="space-y-3">
  <!-- Compact metrics strip -->
  <div class="rounded-base border-2 border-black bg-primary-500 px-4 py-2 flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-2 flex-wrap">
      <Activity class="w-4 h-4 text-white" />
      <span class="text-sm font-black text-white uppercase tracking-wider">Trace Waterfall</span>
      <span class="text-[11px] font-mono text-primary-100 flex items-center gap-1">
        <Hash class="w-3 h-3" />{data.trace_id.slice(0, 12)}…
      </span>
    </div>
    <div class="flex items-center gap-2 text-[11px] font-mono text-white">
      <span class="px-2 py-0.5 bg-surface-50 border-2 border-black rounded-base text-primary-900 font-bold">
        {data.spans.length} spans
      </span>
      <span class="px-2 py-0.5 bg-surface-50 border-2 border-black rounded-base text-primary-900 font-bold flex items-center gap-1">
        <Clock class="w-3 h-3" /> {fmtMs(totalDurationMs)}
      </span>
      <span class="px-2 py-0.5 bg-surface-50 border-2 border-black rounded-base text-primary-900 font-bold flex items-center gap-1">
        <Cpu class="w-3 h-3" /> {fmtCompact(totalTokens)}t
      </span>
      <span class="px-2 py-0.5 bg-warning-200 border-2 border-black rounded-base text-primary-900 font-bold flex items-center gap-1">
        <Coins class="w-3 h-3" /> {fmtUsd(traceCost)}
      </span>
      {#if data.spans.filter((s) => s.error_type).length > 0}
        <span class="px-2 py-0.5 bg-error-300 border-2 border-black rounded-base text-error-900 font-bold flex items-center gap-1">
          <AlertTriangle class="w-3 h-3" /> {data.spans.filter((s) => s.error_type).length}
        </span>
      {/if}
    </div>
  </div>

  <!-- Waterfall -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center justify-between">
      <span class="text-xs font-black uppercase tracking-wide text-primary-800">Span Timeline</span>
      <div class="flex items-center gap-3 text-[10px] font-mono">
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-primary-500 border border-black"></span>agent</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-success-400 border border-black"></span>openai</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-tertiary-400 border border-black"></span>anthropic</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-warning-400 border border-black"></span>tool</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-error-400 border border-black"></span>error</span>
      </div>
    </div>

    <!-- Time axis -->
    <div class="grid grid-cols-[280px_1fr] border-b-2 border-black bg-surface-100">
      <div class="px-2 py-1 border-r-2 border-black text-[10px] font-black uppercase text-primary-700">Span</div>
      <div class="px-2 py-1 relative text-[10px] font-mono text-gray-700">
        <div class="flex justify-between">
          <span>0 ms</span>
          <span>{fmtMs(totalDurationMs * 0.25)}</span>
          <span>{fmtMs(totalDurationMs * 0.5)}</span>
          <span>{fmtMs(totalDurationMs * 0.75)}</span>
          <span>{fmtMs(totalDurationMs)}</span>
        </div>
      </div>
    </div>

    <!-- Rows -->
    <div class="max-h-[420px] overflow-auto">
      {#each orderedSpans as s}
        {@const Icon = spanIconFor(s)}
        {@const depth = depthMap.get(s.span_id) ?? 0}
        {@const active = s.span_id === selectedSpanId}
        <button
          type="button"
          class="grid grid-cols-[280px_1fr] w-full border-b border-gray-300 transition-colors duration-100 {active ? 'bg-primary-100' : 'hover:bg-primary-50'}"
          onclick={() => (selectedSpanId = s.span_id)}
        >
          <!-- Label column -->
          <div class="px-2 py-1.5 border-r-2 border-black flex items-center gap-1.5 min-w-0" style="padding-left: {0.5 + depth * 0.9}rem;">
            <Icon class="w-3 h-3 text-primary-700 shrink-0" />
            <div class="min-w-0 text-left">
              <div class="text-[11px] font-mono font-black text-primary-900 truncate">
                {s.label ?? s.operation_name ?? s.span_id.slice(0, 8)}
              </div>
              <div class="text-[9px] font-mono text-gray-700 truncate">
                {s.span_id.slice(0, 8)}{s.request_model ? ` · ${s.request_model}` : ''}{s.tool_name && !s.request_model ? ` · ${s.tool_name}` : ''}
              </div>
            </div>
          </div>
          <!-- Bar column -->
          <div class="relative h-9 px-2">
            <div
              class="absolute top-1.5 h-6 border-2 rounded-base flex items-center justify-end pr-1.5 {barColor(s)}"
              style="left: calc({offsetPct(s)}% + 0.5rem); width: max(28px, {widthPct(s)}%);"
            >
              <span class="text-[9px] font-mono font-bold text-primary-900 truncate">{fmtMs(s.duration_ms)}</span>
            </div>
            {#if s.error_type}
              <span
                class="absolute top-1 px-1 bg-error-300 border border-black rounded-base text-[8px] font-black text-error-900"
                style="left: calc({offsetPct(s)}% + {widthPct(s)}% + 0.6rem);"
              >ERR</span>
            {/if}
          </div>
        </button>
      {/each}
    </div>
  </div>

  <!-- Selected span detail (compact, full-width) -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="px-3 py-2 border-b-2 border-black bg-primary-500 flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="text-[10px] font-black uppercase tracking-widest text-primary-100">selected span</div>
        <div class="text-base font-black text-white truncate">
          {selectedSpan.label ?? selectedSpan.operation_name ?? selectedSpan.span_id.slice(0, 8)}
        </div>
        <div class="text-[10px] font-mono text-primary-100 truncate">
          {selectedSpan.span_id} · parent {selectedSpan.parent_span_id?.slice(0, 8) ?? 'root'}
          {selectedSpan.provider_name ? ` · ${selectedSpan.provider_name}` : ''}
        </div>
      </div>
      <div class="text-right text-[11px] font-mono text-white">
        <div class="font-black text-base">{fmtMs(selectedSpan.duration_ms)}</div>
        {#if selectedSpan.input_tokens || selectedSpan.output_tokens}
          <div class="text-primary-100">
            {fmtInt(selectedSpan.input_tokens ?? 0)} in / {fmtInt(selectedSpan.output_tokens ?? 0)} out
          </div>
        {/if}
      </div>
    </div>

    <!-- Side-by-side detail grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 divide-y-2 lg:divide-y-0 lg:divide-x-2 divide-black">
      <!-- Attributes -->
      <div class="p-3 max-h-[420px] overflow-auto">
        <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2">Attributes</div>
        <div class="grid grid-cols-1 gap-1 text-[11px]">
          {#each [
            { k: 'service_name', v: selectedSpan.service_name },
            { k: 'operation_name', v: selectedSpan.operation_name ?? '—' },
            { k: 'provider_name', v: selectedSpan.provider_name ?? '—' },
            { k: 'request_model', v: selectedSpan.request_model ?? '—' },
            { k: 'response_model', v: selectedSpan.response_model ?? '—' },
            { k: 'response_id', v: selectedSpan.response_id ?? '—' },
            { k: 'agent_name', v: selectedSpan.agent_name ?? '—' },
            { k: 'agent_version', v: selectedSpan.agent_version ?? '—' },
            { k: 'conversation_id', v: selectedSpan.conversation_id ?? '—' },
            { k: 'tool_name', v: selectedSpan.tool_name ?? '—' },
            { k: 'tool_call_id', v: selectedSpan.tool_call_id ?? '—' },
            { k: 'finish_reasons', v: selectedSpan.finish_reasons.join(', ') || '—' },
            { k: 'temperature', v: selectedSpan.request_temperature ?? '—' },
            { k: 'max_tokens', v: selectedSpan.request_max_tokens ?? '—' },
            { k: 'top_p', v: selectedSpan.request_top_p ?? '—' },
            { k: 'server_address', v: selectedSpan.server_address ?? '—' },
            { k: 'server_port', v: selectedSpan.server_port ?? '—' },
            { k: 'error_type', v: selectedSpan.error_type ?? '—' }
          ] as row}
            <div class="flex items-baseline gap-2 border-b border-gray-300 py-0.5">
              <span class="text-[9px] font-black text-primary-700 uppercase tracking-widest w-32 shrink-0">{row.k}</span>
              <span class="font-mono text-primary-900 break-all flex-1">{row.v}</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- Messages -->
      <div class="p-3 max-h-[420px] overflow-auto">
        <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2">Messages</div>
        {#if selectedSpan.system_instructions}
          <div class="mb-2">
            <div class="text-[9px] font-black uppercase text-primary-700 mb-1">system</div>
            <pre class="text-[10px] bg-primary-50 border-2 border-black rounded-base p-2 whitespace-pre-wrap font-mono text-primary-900 max-h-24 overflow-auto">{selectedSpan.system_instructions}</pre>
          </div>
        {/if}
        {#if selectedSpan.input_messages}
          <div class="mb-2">
            <div class="text-[9px] font-black uppercase text-primary-700 mb-1">input</div>
            <pre class="text-[10px] bg-surface-100 border-2 border-black rounded-base p-2 overflow-auto font-mono text-primary-900 max-h-40">{pretty(selectedSpan.input_messages)}</pre>
          </div>
        {/if}
        {#if selectedSpan.output_messages}
          <div class="mb-2">
            <div class="text-[9px] font-black uppercase text-primary-700 mb-1">output</div>
            <pre class="text-[10px] bg-success-100 border-2 border-black rounded-base p-2 overflow-auto font-mono text-primary-900 max-h-40">{pretty(selectedSpan.output_messages)}</pre>
          </div>
        {/if}
        {#if !selectedSpan.input_messages && !selectedSpan.output_messages && !selectedSpan.system_instructions}
          <div class="text-center text-gray-500 italic text-xs py-4">no messages captured</div>
        {/if}
      </div>

      <!-- Eval + Tool defs -->
      <div class="p-3 max-h-[420px] overflow-auto">
        <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2 flex items-center gap-1">
          <BadgeCheck class="w-3 h-3" /> Eval Results
        </div>
        {#if selectedSpan.eval_results.length === 0}
          <div class="text-center text-gray-500 italic text-xs py-2 mb-2">no evals</div>
        {:else}
          <div class="space-y-2 mb-3">
            {#each selectedSpan.eval_results as e}
              <div class="border-2 border-black rounded-base bg-success-50 p-2">
                <div class="flex items-center justify-between mb-0.5">
                  <span class="font-black text-primary-900 text-xs">{e.name}</span>
                  {#if e.score_value != null}
                    <span class="font-mono font-black text-primary-900 text-sm">{e.score_value}</span>
                  {/if}
                </div>
                {#if e.score_label}
                  <span class="px-1.5 py-0.5 bg-primary-200 border border-black rounded-base text-[10px] font-bold">{e.score_label}</span>
                {/if}
                {#if e.explanation}
                  <div class="text-[11px] text-primary-800 mt-1">{e.explanation}</div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}

        {#if selectedSpan.tool_definitions}
          <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-1 flex items-center gap-1">
            <Wrench class="w-3 h-3" /> tool_definitions
          </div>
          <pre class="text-[10px] bg-surface-100 border-2 border-black rounded-base p-2 overflow-auto font-mono text-primary-900 max-h-32">{pretty(selectedSpan.tool_definitions)}</pre>
        {/if}
      </div>
    </div>
  </div>
</div>
