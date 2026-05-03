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
    Database,
    Hash,
    MessageSquare,
    Server,
    Settings2,
    Wrench
  } from 'lucide-svelte';
  import ChartCard from '$lib/components/card/agent/observability/GenAiChartCard.svelte';
  import {
    buildOperationBarChart,
    buildSpanDurationBar
  } from './charts';
  import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from './format';
  import type { GenAiSpanRecord, GenAiTraceMetricsResponse } from './types';

  let { data }: { data: GenAiTraceMetricsResponse } = $props();

  const summary = $derived(data.agent_dashboard.summary);
  const traceCost = $derived(data.agent_dashboard.buckets[0]?.total_cost ?? 0);
  const totalTokens = $derived(
    summary.total_input_tokens + summary.total_output_tokens
  );
  const errorCount = $derived(
    data.spans.filter((s) => s.error_type).length
  );
  const evalCount = $derived(
    data.spans.reduce((a, s) => a + s.eval_results.length, 0)
  );
  const avgEvalScore = $derived(
    (() => {
      const scores = data.spans.flatMap((s) =>
        s.eval_results
          .map((e) => e.score_value)
          .filter((v): v is number => v != null && v <= 1)
      );
      if (scores.length === 0) return null;
      return scores.reduce((a, b) => a + b, 0) / scores.length;
    })()
  );

  const tokIn = $derived(summary.total_input_tokens);
  const tokOut = $derived(summary.total_output_tokens);
  const tokCC = $derived(summary.total_cache_creation_tokens);
  const tokCR = $derived(summary.total_cache_read_tokens);
  const tokSum = $derived(Math.max(1, tokIn + tokOut + tokCC + tokCR));

  const conversationId = $derived(
    data.spans.find((s) => s.conversation_id)?.conversation_id ?? '—'
  );
  const agentName = $derived(
    data.spans.find((s) => s.agent_name)?.agent_name ?? '—'
  );
  const agentVersion = $derived(
    data.spans.find((s) => s.agent_version)?.agent_version ?? null
  );

  type SpanTab =
    | 'overview'
    | 'messages'
    | 'tool'
    | 'request'
    | 'server'
    | 'eval'
    | 'raw';

  let selectedSpanId = $state<string>(
    (data.spans.find((s) => s.input_messages) ?? data.spans[0])?.span_id ?? ''
  );
  let activeTab = $state<SpanTab>('overview');

  const selectedSpan = $derived(
    data.spans.find((s) => s.span_id === selectedSpanId) ?? data.spans[0]
  );

  function selectSpan(s: GenAiSpanRecord) {
    selectedSpanId = s.span_id;
  }

  function pretty(s: string | null): string {
    if (!s) return '—';
    try {
      return JSON.stringify(JSON.parse(s), null, 2);
    } catch {
      return s;
    }
  }

  function statusPill(s: GenAiSpanRecord): { label: string; cls: string } {
    if (s.error_type) {
      return { label: 'ERR', cls: 'bg-error-300 text-error-900 border-error-700' };
    }
    return { label: 'OK', cls: 'bg-success-300 text-primary-900 border-primary-800' };
  }

  function spanIconFor(s: GenAiSpanRecord) {
    if (s.tool_name) return Wrench;
    if (s.operation_name === 'invoke_agent') return Bot;
    if (s.operation_name === 'embeddings') return Boxes;
    if (s.provider_name) return Cpu;
    return Activity;
  }

  const tabs: { key: SpanTab; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'messages', label: 'Messages' },
    { key: 'tool', label: 'Tool' },
    { key: 'request', label: 'Request' },
    { key: 'server', label: 'Server' },
    { key: 'eval', label: 'Eval' },
    { key: 'raw', label: 'Raw' }
  ];
</script>

<div class="space-y-3">
  <!-- Slim header -->
  <div class="rounded-base border-2 border-black bg-primary-500 px-4 py-2 flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-2 flex-wrap">
      <Activity class="w-4 h-4 text-white" />
      <span class="text-sm font-black text-white uppercase tracking-wider">Trace Metrics</span>
      <span class="text-[11px] font-mono text-primary-100 flex items-center gap-1">
        <Hash class="w-3 h-3" />
        {data.trace_id.slice(0, 12)}…{data.trace_id.slice(-4)}
      </span>
      <span class="text-[11px] font-mono text-primary-100 flex items-center gap-1">
        <MessageSquare class="w-3 h-3" /> {conversationId}
      </span>
      <span class="text-[11px] font-mono text-primary-100 flex items-center gap-1">
        <Bot class="w-3 h-3" /> {agentName}{agentVersion ? `@${agentVersion}` : ''}
      </span>
    </div>
    <div class="flex gap-1.5">
      {#if data.spans_truncated}
        <span class="px-2 py-0.5 bg-warning-200 border-2 border-black rounded-base text-[11px] font-bold text-primary-900">truncated</span>
      {/if}
      {#if data.sensitive_content_redacted}
        <span class="px-2 py-0.5 bg-error-200 border-2 border-black rounded-base text-[11px] font-bold text-primary-900">redacted</span>
      {/if}
      <span class="px-2 py-0.5 bg-surface-50 border-2 border-black rounded-base text-[11px] font-bold">
        {data.spans.length} spans · cap {data.span_limit}
      </span>
    </div>
  </div>

  <!-- KPI rail -->
  <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
    {#each [
      { label: 'Spans', value: fmtInt(data.spans.length), icon: Activity, accent: 'bg-surface-50' },
      { label: 'Dur', value: fmtMs(summary.p99_duration_ms), icon: Clock, accent: 'bg-surface-50' },
      { label: 'p50', value: fmtMs(summary.p50_duration_ms), icon: Clock, accent: 'bg-surface-50' },
      { label: 'Tokens', value: fmtCompact(totalTokens), icon: Cpu, accent: 'bg-surface-50' },
      { label: 'In/Out', value: `${fmtCompact(summary.total_input_tokens)}/${fmtCompact(summary.total_output_tokens)}`, icon: Cpu, accent: 'bg-surface-50' },
      { label: 'Spend', value: fmtUsd(traceCost), icon: Coins, accent: 'bg-warning-100' },
      { label: 'Err', value: errorCount > 0 ? fmtInt(errorCount) : '0', icon: AlertTriangle, accent: errorCount > 0 ? 'bg-error-100' : 'bg-surface-50' },
      { label: 'Eval', value: avgEvalScore != null ? `${(avgEvalScore * 100).toFixed(0)}% · ${evalCount}` : `${evalCount}`, icon: BadgeCheck, accent: 'bg-success-100' }
    ] as kpi}
      <div class="rounded-base border-2 border-black shadow-small {kpi.accent} px-2 py-1.5">
        <div class="flex items-center gap-1 text-[9px] font-black text-primary-700 uppercase tracking-widest">
          <kpi.icon class="w-2.5 h-2.5" /> {kpi.label}
        </div>
        <div class="text-base font-black text-black leading-tight truncate">{kpi.value}</div>
      </div>
    {/each}
  </div>

  <!-- Token mix bar (compact, full-width, no canvas oversize) -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center justify-between">
      <span class="text-xs font-black uppercase tracking-wide text-primary-800">Token Mix</span>
      <span class="text-[11px] font-mono text-primary-700">{fmtCompact(tokSum)} total</span>
    </div>
    <div class="p-3 space-y-2">
      <div class="flex w-full h-5 border-2 border-black rounded-base overflow-hidden">
        <div class="bg-primary-500" style="width: {(tokIn / tokSum) * 100}%" title="input"></div>
        <div class="bg-success-400" style="width: {(tokOut / tokSum) * 100}%" title="output"></div>
        <div class="bg-tertiary-400" style="width: {(tokCC / tokSum) * 100}%" title="cache_create"></div>
        <div class="bg-warning-400" style="width: {(tokCR / tokSum) * 100}%" title="cache_read"></div>
      </div>
      <div class="flex flex-wrap gap-3 text-[11px] font-mono">
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-primary-500 border border-black"></span>input {fmtCompact(tokIn)} ({((tokIn / tokSum) * 100).toFixed(1)}%)</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-success-400 border border-black"></span>output {fmtCompact(tokOut)} ({((tokOut / tokSum) * 100).toFixed(1)}%)</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-tertiary-400 border border-black"></span>cache_create {fmtCompact(tokCC)} ({((tokCC / tokSum) * 100).toFixed(1)}%)</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-warning-400 border border-black"></span>cache_read {fmtCompact(tokCR)} ({((tokCR / tokSum) * 100).toFixed(1)}%)</span>
      </div>
    </div>
  </div>

  <!-- Two-up chart row -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
    <ChartCard
      title="Operations"
      subtitle="span count"
      height="h-44"
      configFn={() => buildOperationBarChart(data.operation_breakdown.operations)}
    />
    <ChartCard
      title="Span Duration"
      subtitle="ms · slowest first"
      height="h-44"
      configFn={() => buildSpanDurationBar(data.spans)}
    />
  </div>

  <!-- Tables row: Models / Tools / Errors -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <Cpu class="w-3 h-3 text-primary-700" />
        <span class="text-xs font-black uppercase tracking-wide text-primary-800">Models</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr class="text-left">
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px]">Model</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Spans</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">In</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Out</th>
          </tr>
        </thead>
        <tbody>
          {#each data.model_usage.models as m}
            <tr class="border-b border-gray-200 hover:bg-primary-50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[160px]">{m.model}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtInt(m.span_count)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(m.total_input_tokens)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(m.total_output_tokens)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <Wrench class="w-3 h-3 text-primary-700" />
        <span class="text-xs font-black uppercase tracking-wide text-primary-800">Tools</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr class="text-left">
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px]">Tool</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Calls</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Avg</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">err</th>
          </tr>
        </thead>
        <tbody>
          {#each data.tool_dashboard.aggregates as t}
            <tr class="border-b border-gray-200 hover:bg-primary-50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[160px]">{t.tool_name}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtInt(t.call_count)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtMs(t.avg_duration_ms)}</td>
              <td class="px-2 py-1 text-right font-mono {t.error_rate > 0 ? 'text-error-700 font-bold' : ''}">{fmtPct(t.error_rate, 0)}</td>
            </tr>
          {/each}
          {#if data.tool_dashboard.aggregates.length === 0}
            <tr><td colspan="4" class="px-2 py-2 text-center text-primary-600 italic">no tool calls</td></tr>
          {/if}
        </tbody>
      </table>
    </div>

    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <AlertTriangle class="w-3 h-3 text-error-700" />
        <span class="text-xs font-black uppercase tracking-wide text-primary-800">Errors</span>
      </div>
      <div class="p-2 space-y-1.5">
        {#each data.error_breakdown.errors as e}
          {@const max = Math.max(...data.error_breakdown.errors.map((x) => x.count))}
          {@const pct = (e.count / max) * 100}
          <div class="flex items-center gap-2">
            <div class="text-[11px] font-mono font-bold text-primary-900 truncate w-32">{e.error_type}</div>
            <div class="flex-1 h-3 bg-surface-100 border border-black rounded-base overflow-hidden">
              <div class="h-full bg-error-300" style="width: {pct}%"></div>
            </div>
            <div class="text-[11px] font-mono text-primary-700 w-10 text-right">{fmtInt(e.count)}</div>
          </div>
        {/each}
        {#if data.error_breakdown.errors.length === 0}
          <div class="text-center text-primary-600 italic text-xs py-2">no errors in trace</div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Span list + detail debug panel -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="px-3 py-1.5 border-b-2 border-black bg-primary-500 flex items-center justify-between">
      <span class="text-xs font-black uppercase tracking-wide text-white">Span Inspector</span>
      <span class="text-[10px] font-mono text-primary-100">click span → inspect</span>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-[280px_1fr] min-h-[420px]">
      <!-- Span list -->
      <div class="border-r-2 border-black overflow-auto max-h-[520px]">
        {#each data.spans as s}
          {@const status = statusPill(s)}
          {@const Icon = spanIconFor(s)}
          {@const active = s.span_id === selectedSpanId}
          <button
            type="button"
            class="w-full text-left px-2.5 py-2 border-b-2 border-black flex items-start gap-2 transition-colors duration-100 {active ? 'bg-primary-200' : 'bg-surface-50 hover:bg-primary-50'}"
            onclick={() => selectSpan(s)}
          >
            <Icon class="w-3.5 h-3.5 mt-0.5 text-primary-700 shrink-0" />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-mono font-black text-primary-900 truncate">
                  {s.label ?? s.operation_name ?? s.span_id.slice(0, 8)}
                </span>
                <span class="px-1 border border-black rounded-base text-[8px] font-black {status.cls}">{status.label}</span>
              </div>
              <div class="text-[9px] font-mono text-primary-700 truncate">
                {s.span_id.slice(0, 8)} · {fmtMs(s.duration_ms)}
                {#if s.request_model}· {s.request_model}{/if}
                {#if s.tool_name && !s.request_model}· {s.tool_name}{/if}
              </div>
            </div>
          </button>
        {/each}
      </div>

      <!-- Detail -->
      <div class="flex flex-col">
        <!-- Tab bar -->
        <div class="flex border-b-2 border-black bg-surface-100 overflow-x-auto">
          {#each tabs as t}
            <button
              type="button"
              class="px-3 py-1.5 text-[11px] font-black uppercase tracking-wide border-r-2 border-black transition-colors duration-100 {activeTab === t.key ? 'bg-primary-300 text-primary-900' : 'text-primary-700 hover:bg-primary-100'}"
              onclick={() => (activeTab = t.key)}
            >
              {t.label}
            </button>
          {/each}
        </div>

        <div class="p-3 overflow-auto max-h-[480px]">
          {#if !selectedSpan}
            <div class="text-center text-primary-600 italic">select a span</div>
          {:else if activeTab === 'overview'}
            <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-[11px]">
              {#each [
                { k: 'span_id', v: selectedSpan.span_id },
                { k: 'parent_span_id', v: selectedSpan.parent_span_id ?? '—' },
                { k: 'service_name', v: selectedSpan.service_name },
                { k: 'operation_name', v: selectedSpan.operation_name ?? '—' },
                { k: 'provider_name', v: selectedSpan.provider_name ?? '—' },
                { k: 'request_model', v: selectedSpan.request_model ?? '—' },
                { k: 'response_model', v: selectedSpan.response_model ?? '—' },
                { k: 'response_id', v: selectedSpan.response_id ?? '—' },
                { k: 'start_time', v: new Date(selectedSpan.start_time).toISOString() },
                { k: 'end_time', v: selectedSpan.end_time ? new Date(selectedSpan.end_time).toISOString() : '—' },
                { k: 'duration_ms', v: fmtMs(selectedSpan.duration_ms) },
                { k: 'status_code', v: String(selectedSpan.status_code) },
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
                <div class="border-2 border-black rounded-base bg-surface-50 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest">{row.k}</div>
                  <div class="font-mono text-primary-900 break-all leading-tight">{row.v}</div>
                </div>
              {/each}
            </div>
          {:else if activeTab === 'messages'}
            <div class="space-y-3">
              <div>
                <div class="text-[10px] font-black uppercase tracking-wide text-primary-700 mb-1">system_instructions</div>
                <pre class="text-[11px] bg-primary-50 border-2 border-black rounded-base p-2 whitespace-pre-wrap font-mono text-primary-900 max-h-40 overflow-auto">{selectedSpan.system_instructions ?? '—'}</pre>
              </div>
              <div>
                <div class="text-[10px] font-black uppercase tracking-wide text-primary-700 mb-1">input_messages</div>
                <pre class="text-[11px] bg-surface-100 border-2 border-black rounded-base p-2 whitespace-pre overflow-auto font-mono text-primary-900 max-h-72">{pretty(selectedSpan.input_messages)}</pre>
              </div>
              <div>
                <div class="text-[10px] font-black uppercase tracking-wide text-primary-700 mb-1">output_messages</div>
                <pre class="text-[11px] bg-success-100 border-2 border-black rounded-base p-2 whitespace-pre overflow-auto font-mono text-primary-900 max-h-72">{pretty(selectedSpan.output_messages)}</pre>
              </div>
            </div>
          {:else if activeTab === 'tool'}
            <div class="space-y-2">
              <div class="grid grid-cols-3 gap-2 text-[11px]">
                <div class="border-2 border-black rounded-base bg-surface-50 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase">tool_name</div>
                  <div class="font-mono">{selectedSpan.tool_name ?? '—'}</div>
                </div>
                <div class="border-2 border-black rounded-base bg-surface-50 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase">tool_type</div>
                  <div class="font-mono">{selectedSpan.tool_type ?? '—'}</div>
                </div>
                <div class="border-2 border-black rounded-base bg-surface-50 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase">tool_call_id</div>
                  <div class="font-mono break-all">{selectedSpan.tool_call_id ?? '—'}</div>
                </div>
              </div>
              <div>
                <div class="text-[10px] font-black uppercase tracking-wide text-primary-700 mb-1 flex items-center gap-1">
                  <Database class="w-3 h-3" /> tool_definitions
                </div>
                <pre class="text-[11px] bg-surface-100 border-2 border-black rounded-base p-2 whitespace-pre overflow-auto font-mono text-primary-900 max-h-72">{pretty(selectedSpan.tool_definitions)}</pre>
              </div>
            </div>
          {:else if activeTab === 'request'}
            <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-[11px]">
              {#each [
                { k: 'temperature', v: selectedSpan.request_temperature },
                { k: 'max_tokens', v: selectedSpan.request_max_tokens },
                { k: 'top_p', v: selectedSpan.request_top_p },
                { k: 'choice_count', v: selectedSpan.request_choice_count },
                { k: 'seed', v: selectedSpan.request_seed },
                { k: 'frequency_penalty', v: selectedSpan.request_frequency_penalty },
                { k: 'presence_penalty', v: selectedSpan.request_presence_penalty }
              ] as row}
                <div class="border-2 border-black rounded-base bg-surface-50 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest flex items-center gap-1">
                    <Settings2 class="w-2.5 h-2.5" /> {row.k}
                  </div>
                  <div class="font-mono text-primary-900">{row.v ?? '—'}</div>
                </div>
              {/each}
              <div class="border-2 border-black rounded-base bg-surface-50 px-2 py-1 col-span-full">
                <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest">stop_sequences</div>
                <div class="font-mono text-primary-900 break-all">{selectedSpan.request_stop_sequences.length ? selectedSpan.request_stop_sequences.join(' · ') : '—'}</div>
              </div>
            </div>
          {:else if activeTab === 'server'}
            <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-[11px]">
              {#each [
                { k: 'server_address', v: selectedSpan.server_address },
                { k: 'server_port', v: selectedSpan.server_port },
                { k: 'openai_api_type', v: selectedSpan.openai_api_type },
                { k: 'openai_service_tier', v: selectedSpan.openai_service_tier },
                { k: 'response_id', v: selectedSpan.response_id },
                { k: 'error_type', v: selectedSpan.error_type }
              ] as row}
                <div class="border-2 border-black rounded-base bg-surface-50 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest flex items-center gap-1">
                    <Server class="w-2.5 h-2.5" /> {row.k}
                  </div>
                  <div class="font-mono text-primary-900 break-all">{row.v ?? '—'}</div>
                </div>
              {/each}
            </div>
          {:else if activeTab === 'eval'}
            {#if selectedSpan.eval_results.length === 0}
              <div class="text-center text-primary-600 italic text-xs py-4">no eval_results recorded for this span</div>
            {:else}
              <div class="space-y-2">
                {#each selectedSpan.eval_results as e}
                  <div class="border-2 border-black rounded-base bg-success-50 p-2">
                    <div class="flex items-center justify-between mb-1">
                      <div class="flex items-center gap-1.5">
                        <BadgeCheck class="w-3 h-3 text-primary-700" />
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
                      <div class="text-[11px] text-primary-800 mb-1">{e.explanation}</div>
                    {/if}
                    {#if e.response_id}
                      <div class="text-[10px] font-mono text-gray-600">response_id: {e.response_id}</div>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          {:else if activeTab === 'raw'}
            <pre class="text-[10px] font-mono bg-surface-100 border-2 border-black rounded-base p-2 overflow-auto max-h-[440px] text-primary-900">{JSON.stringify(selectedSpan, null, 2)}</pre>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>
