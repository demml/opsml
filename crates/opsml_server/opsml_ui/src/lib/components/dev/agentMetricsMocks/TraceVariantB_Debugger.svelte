<script lang="ts">
  import {
    Activity,
    AlertTriangle,
    BadgeCheck,
    Bot,
    Boxes,
    ChevronDown,
    ChevronRight,
    Clock,
    Coins,
    Cpu,
    Database,
    Hash,
    Search,
    Server,
    Settings2,
    Wrench
  } from 'lucide-svelte';
  import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from './format';
  import type { GenAiSpanRecord, GenAiTraceMetricsResponse } from './types';

  let { data }: { data: GenAiTraceMetricsResponse } = $props();

  const summary = $derived(data.agent_dashboard.summary);
  const traceCost = $derived(data.agent_dashboard.buckets[0]?.total_cost ?? 0);
  const errorCount = $derived(data.spans.filter((s) => s.error_type).length);
  const totalTokens = $derived(
    summary.total_input_tokens + summary.total_output_tokens
  );

  let filter = $state('');
  let onlyErrors = $state(false);
  let metricsOpen = $state(false);

  const filteredSpans = $derived(
    data.spans.filter((s) => {
      if (onlyErrors && !s.error_type) return false;
      if (!filter) return true;
      const f = filter.toLowerCase();
      return (
        s.span_id.toLowerCase().includes(f) ||
        (s.operation_name?.toLowerCase().includes(f) ?? false) ||
        (s.tool_name?.toLowerCase().includes(f) ?? false) ||
        (s.label?.toLowerCase().includes(f) ?? false) ||
        (s.request_model?.toLowerCase().includes(f) ?? false)
      );
    })
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
</script>

<div class="space-y-3">
  <!-- Thin metrics ribbon (collapsed metrics dashboard) -->
  <div class="rounded-base border-2 border-black bg-primary-500 overflow-hidden">
    <button
      type="button"
      class="w-full px-4 py-2 flex items-center justify-between hover:bg-primary-600 transition-colors duration-100"
      onclick={() => (metricsOpen = !metricsOpen)}
    >
      <div class="flex items-center gap-3 flex-wrap text-white text-[11px] font-mono">
        {#if metricsOpen}
          <ChevronDown class="w-3.5 h-3.5" />
        {:else}
          <ChevronRight class="w-3.5 h-3.5" />
        {/if}
        <span class="text-sm font-black uppercase tracking-wider">Trace</span>
        <span class="flex items-center gap-1"><Hash class="w-3 h-3" />{data.trace_id.slice(0, 12)}…</span>
        <span class="flex items-center gap-1"><Activity class="w-3 h-3" />{data.spans.length} spans</span>
        <span class="flex items-center gap-1"><Clock class="w-3 h-3" />{fmtMs(summary.p99_duration_ms)}</span>
        <span class="flex items-center gap-1"><Cpu class="w-3 h-3" />{fmtCompact(totalTokens)} tok</span>
        <span class="flex items-center gap-1"><Coins class="w-3 h-3" />{fmtUsd(traceCost)}</span>
        {#if errorCount > 0}
          <span class="flex items-center gap-1 px-1.5 py-0.5 bg-error-300 text-error-900 border border-black rounded-base font-black">
            <AlertTriangle class="w-3 h-3" /> {errorCount} err
          </span>
        {/if}
      </div>
      <span class="text-[10px] text-primary-100 font-mono">{metricsOpen ? 'hide' : 'show'} metrics</span>
    </button>
    {#if metricsOpen}
      <div class="border-t-2 border-black bg-surface-50 p-3 space-y-3">
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {#each [
            { k: 'In tok', v: fmtCompact(summary.total_input_tokens) },
            { k: 'Out tok', v: fmtCompact(summary.total_output_tokens) },
            { k: 'Cache c', v: fmtCompact(summary.total_cache_creation_tokens) },
            { k: 'Cache r', v: fmtCompact(summary.total_cache_read_tokens) },
            { k: 'p50', v: fmtMs(summary.p50_duration_ms) },
            { k: 'p95', v: fmtMs(summary.p95_duration_ms) },
            { k: 'Models', v: fmtInt(data.model_usage.models.length) },
            { k: 'Tools', v: fmtInt(data.tool_dashboard.aggregates.length) }
          ] as kpi}
            <div class="rounded-base border-2 border-black bg-surface-100 px-2 py-1.5">
              <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest">{kpi.k}</div>
              <div class="text-sm font-black text-black">{kpi.v}</div>
            </div>
          {/each}
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <!-- Models -->
          <div class="border-2 border-black rounded-base bg-surface-100 overflow-hidden">
            <div class="px-2 py-1 bg-surface-200 border-b-2 border-black text-[10px] font-black uppercase">Models</div>
            <div class="divide-y divide-gray-300">
              {#each data.model_usage.models as m}
                <div class="px-2 py-1 flex justify-between font-mono">
                  <span class="truncate">{m.model}</span>
                  <span class="text-primary-700">{fmtInt(m.span_count)}× · {fmtCompact(m.total_input_tokens + m.total_output_tokens)}t</span>
                </div>
              {/each}
            </div>
          </div>
          <!-- Tools -->
          <div class="border-2 border-black rounded-base bg-surface-100 overflow-hidden">
            <div class="px-2 py-1 bg-surface-200 border-b-2 border-black text-[10px] font-black uppercase">Tools</div>
            <div class="divide-y divide-gray-300">
              {#each data.tool_dashboard.aggregates as t}
                <div class="px-2 py-1 flex justify-between font-mono">
                  <span class="truncate">{t.tool_name}</span>
                  <span class="text-primary-700">{fmtInt(t.call_count)}× · {fmtMs(t.avg_duration_ms)}</span>
                </div>
              {/each}
            </div>
          </div>
          <!-- Errors -->
          <div class="border-2 border-black rounded-base bg-surface-100 overflow-hidden">
            <div class="px-2 py-1 bg-surface-200 border-b-2 border-black text-[10px] font-black uppercase">Errors</div>
            <div class="divide-y divide-gray-300">
              {#each data.error_breakdown.errors as e}
                <div class="px-2 py-1 flex justify-between font-mono">
                  <span class="truncate">{e.error_type}</span>
                  <span class="text-error-700 font-bold">{fmtInt(e.count)}</span>
                </div>
              {/each}
              {#if data.error_breakdown.errors.length === 0}
                <div class="px-2 py-2 text-center text-primary-600 italic">no errors</div>
              {/if}
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Toolbar -->
  <div class="rounded-base border-2 border-black bg-surface-50 px-3 py-2 flex items-center gap-3 flex-wrap">
    <div class="flex items-center gap-1.5 flex-1 min-w-[200px]">
      <Search class="w-3.5 h-3.5 text-primary-700" />
      <input
        type="text"
        bind:value={filter}
        placeholder="filter spans by id, op, tool, model, label…"
        class="flex-1 bg-surface-100 border-2 border-black rounded-base px-2 py-1 text-xs font-mono focus:outline-none focus:bg-white"
      />
    </div>
    <label class="flex items-center gap-1.5 text-[11px] font-bold cursor-pointer">
      <input type="checkbox" bind:checked={onlyErrors} class="border-2 border-black" />
      <AlertTriangle class="w-3 h-3 text-error-700" />
      errors only
    </label>
    <span class="text-[10px] font-mono text-primary-700">{filteredSpans.length} / {data.spans.length}</span>
  </div>

  <!-- Massive split: span list + detail -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="grid grid-cols-1 lg:grid-cols-[360px_1fr] min-h-[640px]">
      <!-- Span list (denser, more info) -->
      <div class="border-r-2 border-black overflow-auto max-h-[760px]">
        {#each filteredSpans as s}
          {@const Icon = spanIconFor(s)}
          {@const active = s.span_id === selectedSpanId}
          <button
            type="button"
            class="w-full text-left px-3 py-2 border-b-2 border-black flex items-start gap-2 transition-colors duration-100 {active ? 'bg-primary-200' : 'bg-surface-50 hover:bg-primary-50'}"
            onclick={() => (selectedSpanId = s.span_id)}
          >
            <Icon class="w-4 h-4 mt-0.5 text-primary-700 shrink-0" />
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between gap-1">
                <span class="text-[11px] font-mono font-black text-primary-900 truncate">
                  {s.label ?? s.operation_name ?? s.span_id.slice(0, 8)}
                </span>
                {#if s.error_type}
                  <span class="px-1 border border-black rounded-base text-[8px] font-black bg-error-300 text-error-900">ERR</span>
                {/if}
              </div>
              <div class="text-[10px] font-mono text-primary-700 truncate flex items-center gap-1.5">
                <span>{s.span_id.slice(0, 8)}</span>
                <span>·</span>
                <span class="text-primary-800">{fmtMs(s.duration_ms)}</span>
                {#if s.input_tokens || s.output_tokens}
                  <span>·</span>
                  <span>{fmtCompact((s.input_tokens ?? 0) + (s.output_tokens ?? 0))}t</span>
                {/if}
              </div>
              {#if s.request_model || s.tool_name}
                <div class="text-[10px] font-mono text-primary-600 truncate mt-0.5">
                  {s.request_model ?? s.tool_name}
                </div>
              {/if}
              {#if s.eval_results.length > 0}
                <div class="mt-0.5 flex items-center gap-1 text-[9px] text-primary-700 font-bold">
                  <BadgeCheck class="w-2.5 h-2.5" /> {s.eval_results.length} eval
                </div>
              {/if}
            </div>
          </button>
        {/each}
        {#if filteredSpans.length === 0}
          <div class="p-4 text-center text-primary-600 italic text-xs">no spans match filter</div>
        {/if}
      </div>

      <!-- Big detail (single-page, no tabs — everything visible) -->
      <div class="overflow-auto max-h-[760px] divide-y-2 divide-black">
        <!-- Header -->
        <div class="px-4 py-3 bg-surface-100 flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="text-[10px] font-black text-primary-700 uppercase tracking-widest">selected span</div>
            <div class="text-base font-black text-primary-900 truncate">
              {selectedSpan.label ?? selectedSpan.operation_name ?? selectedSpan.span_id.slice(0, 8)}
            </div>
            <div class="text-[11px] font-mono text-primary-700 truncate">
              {selectedSpan.span_id} · parent {selectedSpan.parent_span_id?.slice(0, 8) ?? 'none'}
            </div>
          </div>
          <div class="text-right text-[11px] font-mono text-primary-900">
            <div class="font-black">{fmtMs(selectedSpan.duration_ms)}</div>
            <div class="text-primary-700">status {selectedSpan.status_code}</div>
          </div>
        </div>

        <!-- Overview grid -->
        <div class="p-3">
          <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2">Attributes</div>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-1.5 text-[11px]">
            {#each [
              { k: 'service_name', v: selectedSpan.service_name },
              { k: 'operation_name', v: selectedSpan.operation_name ?? '—' },
              { k: 'provider_name', v: selectedSpan.provider_name ?? '—' },
              { k: 'request_model', v: selectedSpan.request_model ?? '—' },
              { k: 'response_model', v: selectedSpan.response_model ?? '—' },
              { k: 'response_id', v: selectedSpan.response_id ?? '—' },
              { k: 'agent_name', v: selectedSpan.agent_name ?? '—' },
              { k: 'agent_id', v: selectedSpan.agent_id ?? '—' },
              { k: 'agent_version', v: selectedSpan.agent_version ?? '—' },
              { k: 'conversation_id', v: selectedSpan.conversation_id ?? '—' },
              { k: 'data_source_id', v: selectedSpan.data_source_id ?? '—' },
              { k: 'output_type', v: selectedSpan.output_type ?? '—' },
              { k: 'finish_reasons', v: selectedSpan.finish_reasons.join(', ') || '—' },
              { k: 'input_tokens', v: selectedSpan.input_tokens != null ? fmtInt(selectedSpan.input_tokens) : '—' },
              { k: 'output_tokens', v: selectedSpan.output_tokens != null ? fmtInt(selectedSpan.output_tokens) : '—' },
              { k: 'cache_creation', v: selectedSpan.cache_creation_input_tokens != null ? fmtInt(selectedSpan.cache_creation_input_tokens) : '—' },
              { k: 'cache_read', v: selectedSpan.cache_read_input_tokens != null ? fmtInt(selectedSpan.cache_read_input_tokens) : '—' },
              { k: 'error_type', v: selectedSpan.error_type ?? '—' }
            ] as row}
              <div class="border border-black rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest">{row.k}</div>
                <div class="font-mono text-primary-900 break-all leading-tight">{row.v}</div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Request params (if LLM call) -->
        {#if selectedSpan.request_model}
          <div class="p-3">
            <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2 flex items-center gap-1">
              <Settings2 class="w-3 h-3" /> Request Params
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-1.5 text-[11px]">
              {#each [
                { k: 'temperature', v: selectedSpan.request_temperature },
                { k: 'max_tokens', v: selectedSpan.request_max_tokens },
                { k: 'top_p', v: selectedSpan.request_top_p },
                { k: 'choice_count', v: selectedSpan.request_choice_count },
                { k: 'seed', v: selectedSpan.request_seed },
                { k: 'freq_penalty', v: selectedSpan.request_frequency_penalty },
                { k: 'presence_penalty', v: selectedSpan.request_presence_penalty }
              ] as row}
                <div class="border border-black rounded-base bg-surface-100 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase">{row.k}</div>
                  <div class="font-mono text-primary-900">{row.v ?? '—'}</div>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Tool block -->
        {#if selectedSpan.tool_name || selectedSpan.tool_definitions}
          <div class="p-3">
            <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2 flex items-center gap-1">
              <Wrench class="w-3 h-3" /> Tool
            </div>
            <div class="grid grid-cols-3 gap-1.5 text-[11px] mb-2">
              <div class="border border-black rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase">tool_name</div>
                <div class="font-mono">{selectedSpan.tool_name ?? '—'}</div>
              </div>
              <div class="border border-black rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase">tool_type</div>
                <div class="font-mono">{selectedSpan.tool_type ?? '—'}</div>
              </div>
              <div class="border border-black rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase">tool_call_id</div>
                <div class="font-mono break-all">{selectedSpan.tool_call_id ?? '—'}</div>
              </div>
            </div>
            {#if selectedSpan.tool_definitions}
              <div class="text-[10px] font-black uppercase text-primary-700 mb-1 flex items-center gap-1">
                <Database class="w-3 h-3" /> tool_definitions
              </div>
              <pre class="text-[10px] bg-surface-100 border-2 border-black rounded-base p-2 overflow-auto font-mono text-primary-900 max-h-48">{pretty(selectedSpan.tool_definitions)}</pre>
            {/if}
          </div>
        {/if}

        <!-- Messages -->
        {#if selectedSpan.input_messages || selectedSpan.output_messages || selectedSpan.system_instructions}
          <div class="p-3">
            <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2">Messages</div>
            {#if selectedSpan.system_instructions}
              <div class="mb-2">
                <div class="text-[9px] font-black uppercase text-primary-700 mb-1">system</div>
                <pre class="text-[11px] bg-primary-50 border-2 border-black rounded-base p-2 whitespace-pre-wrap font-mono text-primary-900 max-h-32 overflow-auto">{selectedSpan.system_instructions}</pre>
              </div>
            {/if}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
              {#if selectedSpan.input_messages}
                <div>
                  <div class="text-[9px] font-black uppercase text-primary-700 mb-1">input</div>
                  <pre class="text-[10px] bg-surface-100 border-2 border-black rounded-base p-2 overflow-auto font-mono text-primary-900 max-h-64">{pretty(selectedSpan.input_messages)}</pre>
                </div>
              {/if}
              {#if selectedSpan.output_messages}
                <div>
                  <div class="text-[9px] font-black uppercase text-primary-700 mb-1">output</div>
                  <pre class="text-[10px] bg-success-100 border-2 border-black rounded-base p-2 overflow-auto font-mono text-primary-900 max-h-64">{pretty(selectedSpan.output_messages)}</pre>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Server -->
        <div class="p-3">
          <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2 flex items-center gap-1">
            <Server class="w-3 h-3" /> Server
          </div>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-1.5 text-[11px]">
            {#each [
              { k: 'server_address', v: selectedSpan.server_address },
              { k: 'server_port', v: selectedSpan.server_port },
              { k: 'openai_api_type', v: selectedSpan.openai_api_type },
              { k: 'openai_service_tier', v: selectedSpan.openai_service_tier }
            ] as row}
              <div class="border border-black rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase">{row.k}</div>
                <div class="font-mono break-all">{row.v ?? '—'}</div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Eval -->
        {#if selectedSpan.eval_results.length > 0}
          <div class="p-3">
            <div class="text-[10px] font-black uppercase tracking-widest text-primary-700 mb-2 flex items-center gap-1">
              <BadgeCheck class="w-3 h-3" /> Eval Results
            </div>
            <div class="space-y-2">
              {#each selectedSpan.eval_results as e}
                <div class="border-2 border-black rounded-base bg-success-50 p-2">
                  <div class="flex items-center justify-between mb-1">
                    <div class="flex items-center gap-1.5">
                      <span class="font-black text-primary-900 text-xs">{e.name}</span>
                      {#if e.score_label}
                        <span class="px-1.5 py-0.5 bg-primary-200 border border-black rounded-base text-[10px] font-bold">{e.score_label}</span>
                      {/if}
                    </div>
                    {#if e.score_value != null}
                      <span class="font-mono font-black text-primary-900 text-sm">{e.score_value}</span>
                    {/if}
                  </div>
                  {#if e.explanation}
                    <div class="text-[11px] text-primary-800">{e.explanation}</div>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
