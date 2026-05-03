<script lang="ts">
  import type { GenAiTraceMetricsResponse } from '$lib/components/scouter/genai/types';
  import GenAiChartCard from '$lib/components/card/agent/observability/GenAiChartCard.svelte';
  import {
    buildOperationBarChart,
    buildSpanDurationBar,
  } from '$lib/components/card/agent/observability/charts';
  import {
    fmtCompact,
    fmtInt,
    fmtMs,
    fmtUsd,
  } from '$lib/components/card/agent/observability/format';
  import {
    Activity,
    AlertTriangle,
    BadgeCheck,
    Bot,
    Clock,
    Coins,
    Cpu,
    Database,
    Wrench,
  } from 'lucide-svelte';

  let { genai }: { genai: GenAiTraceMetricsResponse } = $props();

  const summary = $derived(genai.agent_dashboard.summary);
  const tokIn = $derived(summary.total_input_tokens);
  const tokOut = $derived(summary.total_output_tokens);
  const tokCC = $derived(summary.total_cache_creation_tokens);
  const tokCR = $derived(summary.total_cache_read_tokens);
  const tokSum = $derived(Math.max(1, tokIn + tokOut + tokCC + tokCR));
  const traceCost = $derived(genai.agent_dashboard.buckets[0]?.total_cost ?? 0);
  const errorCount = $derived(genai.spans.filter((s) => s.error_type).length);
  const evalCount = $derived(
    genai.spans.reduce((a, s) => a + s.eval_results.length, 0),
  );
  const maxErrorCount = $derived(
    genai.error_breakdown.errors.length > 0
      ? Math.max(...genai.error_breakdown.errors.map((e) => e.count))
      : 1,
  );
</script>

<div class="p-3 space-y-3">

  <!-- KPI rail -->
  <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
    {#each [
      { label: 'GenAI Spans', value: fmtInt(genai.spans.length), icon: Activity, accent: 'bg-surface-50' },
      { label: 'p50',         value: fmtMs(summary.p50_duration_ms), icon: Clock, accent: 'bg-surface-50' },
      { label: 'p95',         value: fmtMs(summary.p95_duration_ms), icon: Clock, accent: 'bg-surface-50' },
      { label: 'In / Out',    value: `${fmtCompact(tokIn)} / ${fmtCompact(tokOut)}`, icon: Cpu, accent: 'bg-surface-50' },
      { label: 'Cache',       value: `${fmtCompact(tokCC)} / ${fmtCompact(tokCR)}`, icon: Database, accent: 'bg-surface-50' },
      { label: 'Spend',       value: fmtUsd(traceCost), icon: Coins, accent: 'bg-warning-100' },
      { label: 'Errors',      value: fmtInt(errorCount), icon: AlertTriangle, accent: errorCount > 0 ? 'bg-error-100' : 'bg-surface-50' },
      { label: 'Evals',       value: fmtInt(evalCount), icon: BadgeCheck, accent: 'bg-success-100' },
    ] as kpi (kpi.label)}
      <div class="rounded-base border-2 border-black shadow-small {kpi.accent} px-2 py-1.5">
        <div class="flex items-center gap-1 text-xs font-black text-primary-700 uppercase tracking-widest">
          <kpi.icon class="w-2.5 h-2.5" /> {kpi.label}
        </div>
        <div class="text-sm font-black text-black leading-tight truncate">{kpi.value}</div>
      </div>
    {/each}
  </div>

  <!-- Token mix bar -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center justify-between">
      <span class="text-xs font-black uppercase tracking-wide text-primary-800">Token Mix</span>
      <span class="text-xs font-mono text-primary-700">{fmtCompact(tokSum)} total</span>
    </div>
    <div class="p-2 space-y-1.5">
      <div class="flex w-full h-4 border-2 border-black rounded-base overflow-hidden">
        <div class="bg-primary-500" style="width: {(tokIn / tokSum) * 100}%"></div>
        <div class="bg-success-400" style="width: {(tokOut / tokSum) * 100}%"></div>
        <div class="bg-tertiary-400" style="width: {(tokCC / tokSum) * 100}%"></div>
        <div class="bg-warning-400" style="width: {(tokCR / tokSum) * 100}%"></div>
      </div>
      <div class="flex flex-wrap gap-3 text-xs font-mono text-primary-800">
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-primary-500 border border-black"></span>input {fmtCompact(tokIn)} ({((tokIn / tokSum) * 100).toFixed(1)}%)</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-success-400 border border-black"></span>output {fmtCompact(tokOut)} ({((tokOut / tokSum) * 100).toFixed(1)}%)</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-tertiary-400 border border-black"></span>cache_create {fmtCompact(tokCC)}</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 bg-warning-400 border border-black"></span>cache_read {fmtCompact(tokCR)}</span>
      </div>
    </div>
  </div>

  <!-- 2-up charts -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
    <GenAiChartCard
      title="Operations"
      subtitle="span count"
      height="h-36"
      configFn={() => buildOperationBarChart(genai.operation_breakdown.operations)}
    />
    <GenAiChartCard
      title="Span Duration"
      subtitle="slowest first"
      height="h-36"
      configFn={() => buildSpanDurationBar(genai.spans)}
    />
  </div>

  <!-- 3-column tables: Models / Tools / Errors -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">

    <!-- Models -->
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <Cpu class="w-3 h-3 text-primary-700" />
        <span class="text-xs font-black uppercase text-primary-800">Models</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr>
            <th class="px-2 py-1 text-left font-black text-primary-700 uppercase text-xs">Model</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">Spans</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">In/Out tok</th>
          </tr>
        </thead>
        <tbody>
          {#each genai.model_usage.models as m (m.model)}
            <tr class="border-b border-black/10 hover:bg-primary-100/50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[120px]">{m.model}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-900">{fmtInt(m.span_count)}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-900">{fmtCompact(m.total_input_tokens)}/{fmtCompact(m.total_output_tokens)}</td>
            </tr>
          {/each}
          {#if genai.model_usage.models.length === 0}
            <tr><td colspan="3" class="px-2 py-2 text-center text-primary-600 italic">no model usage</td></tr>
          {/if}
        </tbody>
      </table>
    </div>

    <!-- Tools -->
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <Wrench class="w-3 h-3 text-primary-700" />
        <span class="text-xs font-black uppercase text-primary-800">Tools</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr>
            <th class="px-2 py-1 text-left font-black text-primary-700 uppercase text-xs">Tool</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">Calls</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">Avg ms</th>
          </tr>
        </thead>
        <tbody>
          {#each genai.tool_dashboard.aggregates as t, i (t.tool_name ?? `__null_${i}`)}
            <tr class="border-b border-black/10 hover:bg-primary-100/50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate">{t.tool_name ?? '—'}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-900">{fmtInt(t.call_count)}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-900">{fmtMs(t.avg_duration_ms)}</td>
            </tr>
          {/each}
          {#if genai.tool_dashboard.aggregates.length === 0}
            <tr><td colspan="3" class="px-2 py-2 text-center text-primary-600 italic">no tool calls</td></tr>
          {/if}
        </tbody>
      </table>
    </div>

    <!-- Errors -->
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <AlertTriangle class="w-3 h-3 text-error-700" />
        <span class="text-xs font-black uppercase text-primary-800">Errors</span>
      </div>
      <div class="divide-y divide-black/10">
        {#each genai.error_breakdown.errors as e (e.error_type)}
          <div class="px-2 py-1.5 flex items-center gap-2 text-xs">
            <span class="font-mono font-bold text-primary-900 truncate flex-1">{e.error_type}</span>
            <div class="w-20 h-2.5 bg-surface-100 border border-black rounded-base overflow-hidden">
              <div class="h-full bg-error-300" style="width: {(e.count / maxErrorCount) * 100}%"></div>
            </div>
            <span class="font-mono text-error-700 font-bold w-6 text-right">{fmtInt(e.count)}</span>
          </div>
        {/each}
        {#if genai.error_breakdown.errors.length === 0}
          <div class="px-2 py-3 text-center text-primary-600 italic text-xs">no errors in trace</div>
        {/if}
      </div>
    </div>

  </div>

  <!-- Agent activity -->
  {#if genai.agent_activity.agents.length > 0}
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <Bot class="w-3 h-3 text-primary-700" />
        <span class="text-xs font-black uppercase text-primary-800">Agent Activity</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr>
            <th class="px-2 py-1 text-left font-black text-primary-700 uppercase text-xs">Agent</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">Spans</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">In tok</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">Out tok</th>
            <th class="px-2 py-1 text-right font-black text-primary-700 uppercase text-xs">Conversation</th>
          </tr>
        </thead>
        <tbody>
          {#each genai.agent_activity.agents as a, i (a.agent_id ?? a.agent_name ?? `__agent_${i}`)}
            <tr class="border-b border-black/10 hover:bg-primary-100/50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate">{a.agent_name ?? '—'}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-900">{fmtInt(a.span_count)}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-900">{fmtCompact(a.total_input_tokens)}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-900">{fmtCompact(a.total_output_tokens)}</td>
              <td class="px-2 py-1 text-right font-mono text-primary-700 truncate max-w-[120px]">{a.conversation_id ?? '—'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

</div>
