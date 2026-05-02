<script lang="ts">
  import {
    Activity,
    AlertTriangle,
    Clock,
    Coins,
    Cpu,
    MessageSquare,
    Users,
    Wrench,
    Zap
  } from 'lucide-svelte';
  import ChartCard from './ChartCard.svelte';
  import {
    buildVolumeChart,
    buildLatencyChart,
    buildTokenChart,
    buildCostChart,
    buildErrorRateChart,
    buildToolStackChart
  } from './charts';
  import type { MockMetricsBundle } from './types';
  import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from './format';

  let { bundle }: { bundle: MockMetricsBundle } = $props();

  const summary = $derived(bundle.agent_dashboard.summary);
  const totalCost = $derived(
  );
  const totalTokens = $derived(
    summary.total_input_tokens + summary.total_output_tokens
  );
</script>

<div class="space-y-3">
  <!-- Slim header -->
  <div class="rounded-base border-2 border-black bg-primary-500 px-4 py-2 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <Activity class="w-4 h-4 text-white" />
      <span class="text-sm font-black text-white uppercase tracking-wider">Agent Metrics</span>
      <span class="text-[11px] font-mono text-primary-100">service=research-agent · 60 buckets · 1m</span>
    </div>
    <div class="flex gap-1.5">
      <button class="px-2 py-0.5 bg-surface-50 border-2 border-black rounded-base text-[11px] font-bold">1h</button>
      <button class="px-2 py-0.5 bg-primary-100 border-2 border-black rounded-base text-[11px] font-bold">6h</button>
      <button class="px-2 py-0.5 bg-primary-100 border-2 border-black rounded-base text-[11px] font-bold">24h</button>
      <button class="px-2 py-0.5 bg-primary-100 border-2 border-black rounded-base text-[11px] font-bold">7d</button>
    </div>
  </div>

  <!-- Dense KPI rail (10 cells) -->
  <div class="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2">
    {#each [
      { label: 'Req', value: fmtCompact(summary.total_requests), icon: Zap, accent: 'bg-surface-50' },
      { label: 'Err%', value: fmtPct(summary.overall_error_rate, 2), icon: AlertTriangle, accent: summary.overall_error_rate > 0.02 ? 'bg-error-100' : 'bg-surface-50' },
      { label: 'p50', value: fmtMs(summary.p50_duration_ms), icon: Clock, accent: 'bg-surface-50' },
      { label: 'p95', value: fmtMs(summary.p95_duration_ms), icon: Clock, accent: 'bg-surface-50' },
      { label: 'p99', value: fmtMs(summary.p99_duration_ms), icon: Clock, accent: 'bg-surface-50' },
      { label: 'Spend', value: fmtUsd(totalCost), icon: Coins, accent: 'bg-warning-100' },
      { label: 'Tok', value: fmtCompact(totalTokens), icon: Cpu, accent: 'bg-surface-50' },
      { label: 'In', value: fmtCompact(summary.total_input_tokens), icon: Cpu, accent: 'bg-surface-50' },
      { label: 'Out', value: fmtCompact(summary.total_output_tokens), icon: Cpu, accent: 'bg-surface-50' },
      { label: 'Convo', value: fmtInt(summary.unique_conversation_count), icon: MessageSquare, accent: 'bg-surface-50' }
    ] as kpi}
      <div class="rounded-base border-2 border-black shadow-small {kpi.accent} px-2 py-1.5">
        <div class="flex items-center gap-1 text-[9px] font-black text-primary-700 uppercase tracking-widest">
          <kpi.icon class="w-2.5 h-2.5" /> {kpi.label}
        </div>
        <div class="text-base font-black text-black leading-tight">{kpi.value}</div>
      </div>
    {/each}
  </div>

  <!-- Compact 4-up chart grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
    <ChartCard
      title="Volume"
      subtitle="success · err"
      height="h-40"
      configFn={() => buildVolumeChart(bundle.agent_dashboard.buckets)}
    />
    <ChartCard
      title="Latency"
      subtitle="p50/95/99"
      height="h-40"
      configFn={() => buildLatencyChart(bundle.agent_dashboard.buckets)}
    />
    <ChartCard
      title="Tokens"
      subtitle="in · out · cache"
      height="h-40"
      configFn={() => buildTokenChart(bundle.agent_dashboard.buckets)}
    />
    <ChartCard
      title="Spend"
      subtitle="$ / bucket"
      height="h-40"
      configFn={() => buildCostChart(bundle.agent_dashboard.buckets)}
    />
  </div>

  <!-- Two-up secondary -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <ChartCard
      title="Errors"
      subtitle="% per bucket"
      height="h-44"
      configFn={() => buildErrorRateChart(bundle.agent_dashboard.buckets)}
    />
    <ChartCard
      title="Tool Calls"
      subtitle="stacked"
      height="h-44"
      configFn={() => buildToolStackChart(bundle.tool_dashboard.time_series)}
    />
  </div>

  <!-- Three dense panels: Models / Tools / Errors -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
    <!-- Models -->
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100">
        <span class="text-xs font-black uppercase tracking-wide text-primary-800">Models</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr class="text-left">
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px]">Model</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Spans</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">p95</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">err</th>
          </tr>
        </thead>
        <tbody>
          {#each bundle.model_usage as m}
            <tr class="border-b border-gray-200 hover:bg-primary-50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[140px]">{m.model}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(m.span_count)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtMs(m.p95_duration_ms)}</td>
              <td class="px-2 py-1 text-right font-mono {m.error_rate > 0.01 ? 'text-error-700 font-bold' : ''}">{fmtPct(m.error_rate, 1)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Tools -->
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
          {#each bundle.tool_dashboard.aggregates as t}
            <tr class="border-b border-gray-200 hover:bg-primary-50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[140px]">{t.tool_name}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(t.call_count)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtMs(t.avg_duration_ms)}</td>
              <td class="px-2 py-1 text-right font-mono {t.error_rate > 0.02 ? 'text-error-700 font-bold' : ''}">{fmtPct(t.error_rate, 1)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Errors -->
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <AlertTriangle class="w-3 h-3 text-error-700" />
        <span class="text-xs font-black uppercase tracking-wide text-primary-800">Errors</span>
      </div>
      <div class="p-2 space-y-1.5">
        {#each bundle.errors as e}
          {@const max = Math.max(...bundle.errors.map((x) => x.count))}
          {@const pct = (e.count / max) * 100}
          <div class="flex items-center gap-2">
            <div class="text-[11px] font-mono font-bold text-primary-900 truncate w-32">{e.error_type}</div>
            <div class="flex-1 h-3 bg-surface-100 border border-black rounded-base overflow-hidden">
              <div class="h-full bg-error-300" style="width: {pct}%"></div>
            </div>
            <div class="text-[11px] font-mono text-gray-700 w-10 text-right">{fmtInt(e.count)}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Operations + Agents (compact dual table) -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100">
        <span class="text-xs font-black uppercase tracking-wide text-primary-800">Operations</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr class="text-left">
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px]">Operation</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Spans</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Avg</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">err</th>
          </tr>
        </thead>
        <tbody>
          {#each bundle.operation_breakdown as op}
            <tr class="border-b border-gray-200 hover:bg-primary-50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[180px]">{op.operation_name}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(op.span_count)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtMs(op.avg_duration_ms)}</td>
              <td class="px-2 py-1 text-right font-mono {op.error_rate > 0.02 ? 'text-error-700 font-bold' : ''}">{fmtPct(op.error_rate, 1)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
        <Users class="w-3 h-3 text-primary-700" />
        <span class="text-xs font-black uppercase tracking-wide text-primary-800">Agents</span>
      </div>
      <table class="w-full text-xs">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr class="text-left">
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px]">Agent</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Spans</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">In</th>
            <th class="px-2 py-1 font-black text-primary-700 uppercase text-[9px] text-right">Out</th>
          </tr>
        </thead>
        <tbody>
          {#each bundle.agents as a}
            <tr class="border-b border-gray-200 hover:bg-primary-50">
              <td class="px-2 py-1 font-mono font-bold text-primary-900 truncate max-w-[180px]">{a.agent_name}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(a.span_count)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(a.total_input_tokens)}</td>
              <td class="px-2 py-1 text-right font-mono">{fmtCompact(a.total_output_tokens)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
