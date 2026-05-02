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
    Zap,
    ChevronDown
  } from 'lucide-svelte';
  import ChartCard from './ChartCard.svelte';
  import {
    buildVolumeChart,
    buildLatencyChart,
    buildTokenChart,
    buildCostDonut,
    buildErrorRateChart,
    buildToolStackChart
  } from './charts';
  import type { MockMetricsBundle } from './types';
  import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from './format';

  let { bundle }: { bundle: MockMetricsBundle } = $props();

  const summary = $derived(bundle.agent_dashboard.summary);
  const totalCost = $derived(
    summary.cost_by_model.reduce((a, b) => a + (b.total_cost ?? 0), 0)
  );
</script>

<div class="space-y-5">
  <!-- Header strip: agent identity + filter bar -->
  <div class="rounded-base border-2 border-black shadow bg-primary-100 p-4 flex flex-wrap items-center justify-between gap-3">
    <div class="flex items-center gap-3">
      <div class="p-2 bg-primary-500 border-2 border-black rounded-base">
        <Activity class="w-5 h-5 text-white" />
      </div>
      <div>
        <h2 class="text-lg font-black text-black uppercase tracking-wide">Agent Metrics</h2>
        <p class="text-xs font-mono text-primary-700">service_name=research-agent · live</p>
      </div>
    </div>
    <div class="flex flex-wrap gap-2">
      <button class="flex items-center gap-2 px-3 py-1.5 bg-surface-50 border-2 border-black rounded-base shadow-small text-xs font-bold text-primary-800">
        <Clock class="w-3.5 h-3.5" /> Past 1 Hour <ChevronDown class="w-3 h-3" />
      </button>
      <button class="flex items-center gap-2 px-3 py-1.5 bg-surface-50 border-2 border-black rounded-base shadow-small text-xs font-bold text-primary-800">
        Agent: all <ChevronDown class="w-3 h-3" />
      </button>
      <button class="flex items-center gap-2 px-3 py-1.5 bg-surface-50 border-2 border-black rounded-base shadow-small text-xs font-bold text-primary-800">
        Provider: all <ChevronDown class="w-3 h-3" />
      </button>
    </div>
  </div>

  <!-- KPI Strip (7 tiles) -->
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-primary-700 uppercase tracking-wider">
        <Zap class="w-3.5 h-3.5" /> Requests
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtCompact(summary.total_requests)}</div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-error-100 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-error-900 uppercase tracking-wider">
        <AlertTriangle class="w-3.5 h-3.5" /> Error Rate
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtPct(summary.overall_error_rate, 2)}</div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-primary-700 uppercase tracking-wider">
        <Clock class="w-3.5 h-3.5" /> p95
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtMs(summary.p95_duration_ms)}</div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="text-xs font-black text-primary-700 uppercase tracking-wider">p50</div>
      <div class="text-2xl font-black text-black mt-1">{fmtMs(summary.p50_duration_ms)}</div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-warning-100 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-black uppercase tracking-wider">
        <Coins class="w-3.5 h-3.5" /> Spend
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtUsd(totalCost)}</div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-primary-700 uppercase tracking-wider">
        <Cpu class="w-3.5 h-3.5" /> Tokens
      </div>
      <div class="text-2xl font-black text-black mt-1">
        {fmtCompact(summary.total_input_tokens + summary.total_output_tokens)}
      </div>
      <div class="text-[10px] font-mono text-gray-700 mt-0.5">
        {fmtCompact(summary.total_input_tokens)} in · {fmtCompact(summary.total_output_tokens)} out
      </div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-primary-700 uppercase tracking-wider">
        <MessageSquare class="w-3.5 h-3.5" /> Convos
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtInt(summary.unique_conversation_count)}</div>
    </div>
  </div>

  <!-- Full-width primary time series stack -->
  <ChartCard
    title="Request Volume"
    subtitle="success vs error · stacked"
    configFn={() => buildVolumeChart(bundle.agent_dashboard.buckets)}
  />

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
    <ChartCard
      title="Latency"
      subtitle="p50 · p95 · p99"
      configFn={() => buildLatencyChart(bundle.agent_dashboard.buckets)}
    />
    <ChartCard
      title="Error Rate"
      subtitle="% per bucket"
      configFn={() => buildErrorRateChart(bundle.agent_dashboard.buckets)}
    />
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
    <div class="lg:col-span-2">
      <ChartCard
        title="Token Usage"
        subtitle="input · output · cache_read"
        configFn={() => buildTokenChart(bundle.agent_dashboard.buckets)}
      />
    </div>
    <ChartCard
      title="Cost by Model"
      subtitle="window total"
      configFn={() => buildCostDonut(summary.cost_by_model)}
    />
  </div>

  <!-- Tables side-by-side: model usage + tools -->
  <div class="grid grid-cols-1 xl:grid-cols-2 gap-5">
    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-4 py-2.5 border-b-2 border-black bg-surface-100">
        <span class="text-sm font-black uppercase tracking-wide text-primary-800">Model Usage</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-100 border-b-2 border-black">
            <tr class="text-left">
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">Model</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">Provider</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Spans</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">In tok</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Out tok</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">p50</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">p95</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">err</th>
            </tr>
          </thead>
          <tbody>
            {#each bundle.model_usage as m}
              <tr class="border-b border-gray-200 hover:bg-primary-50">
                <td class="px-3 py-2 font-mono font-bold text-primary-900">{m.model}</td>
                <td class="px-3 py-2 text-gray-700">{m.provider_name ?? '—'}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtCompact(m.span_count)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtCompact(m.total_input_tokens)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtCompact(m.total_output_tokens)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtMs(m.p50_duration_ms)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtMs(m.p95_duration_ms)}</td>
                <td class="px-3 py-2 text-right font-mono {m.error_rate > 0.01 ? 'text-error-700 font-bold' : ''}">{fmtPct(m.error_rate)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>

    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-4 py-2.5 border-b-2 border-black bg-surface-100 flex items-center gap-2">
        <Wrench class="w-4 h-4 text-primary-700" />
        <span class="text-sm font-black uppercase tracking-wide text-primary-800">Tool Activity</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-100 border-b-2 border-black">
            <tr class="text-left">
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">Tool</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">Type</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Calls</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Avg</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">err</th>
            </tr>
          </thead>
          <tbody>
            {#each bundle.tool_dashboard.aggregates as t}
              <tr class="border-b border-gray-200 hover:bg-primary-50">
                <td class="px-3 py-2 font-mono font-bold text-primary-900">{t.tool_name}</td>
                <td class="px-3 py-2 text-gray-700">{t.tool_type}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtCompact(t.call_count)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtMs(t.avg_duration_ms)}</td>
                <td class="px-3 py-2 text-right font-mono {t.error_rate > 0.02 ? 'text-error-700 font-bold' : ''}">{fmtPct(t.error_rate)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Operations + Errors -->
  <div class="grid grid-cols-1 xl:grid-cols-3 gap-5">
    <div class="xl:col-span-2 rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-4 py-2.5 border-b-2 border-black bg-surface-100">
        <span class="text-sm font-black uppercase tracking-wide text-primary-800">Operations</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-100 border-b-2 border-black">
            <tr class="text-left">
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">Operation</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">Provider</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Spans</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Avg dur</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">In tok</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Out tok</th>
              <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">err</th>
            </tr>
          </thead>
          <tbody>
            {#each bundle.operation_breakdown as op}
              <tr class="border-b border-gray-200 hover:bg-primary-50">
                <td class="px-3 py-2 font-mono font-bold text-primary-900">{op.operation_name}</td>
                <td class="px-3 py-2 text-gray-700">{op.provider_name ?? '—'}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtCompact(op.span_count)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtMs(op.avg_duration_ms)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtCompact(op.total_input_tokens)}</td>
                <td class="px-3 py-2 text-right font-mono">{fmtCompact(op.total_output_tokens)}</td>
                <td class="px-3 py-2 text-right font-mono {op.error_rate > 0.02 ? 'text-error-700 font-bold' : ''}">{fmtPct(op.error_rate)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>

    <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
      <div class="px-4 py-2.5 border-b-2 border-black bg-surface-100 flex items-center gap-2">
        <AlertTriangle class="w-4 h-4 text-error-700" />
        <span class="text-sm font-black uppercase tracking-wide text-primary-800">Error Types</span>
      </div>
      <div class="p-4 space-y-2">
        {#each bundle.errors as e}
          {@const max = Math.max(...bundle.errors.map((x) => x.count))}
          {@const pct = (e.count / max) * 100}
          <div>
            <div class="flex justify-between text-xs font-mono mb-0.5">
              <span class="font-bold text-primary-900">{e.error_type}</span>
              <span class="text-gray-700">{fmtInt(e.count)}</span>
            </div>
            <div class="h-3 bg-surface-100 border border-black rounded-base overflow-hidden">
              <div class="h-full bg-error-300 border-r border-black" style="width: {pct}%"></div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Top agents -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="px-4 py-2.5 border-b-2 border-black bg-surface-100 flex items-center gap-2">
      <Users class="w-4 h-4 text-primary-700" />
      <span class="text-sm font-black uppercase tracking-wide text-primary-800">Active Agents</span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-surface-100 border-b-2 border-black">
          <tr class="text-left">
            <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">Agent</th>
            <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider">ID</th>
            <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Spans</th>
            <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">In tok</th>
            <th class="px-3 py-2 font-black text-primary-700 uppercase text-[10px] tracking-wider text-right">Out tok</th>
          </tr>
        </thead>
        <tbody>
          {#each bundle.agents as a}
            <tr class="border-b border-gray-200 hover:bg-primary-50">
              <td class="px-3 py-2 font-mono font-bold text-primary-900">{a.agent_name}</td>
              <td class="px-3 py-2 text-gray-700 font-mono text-xs">{a.agent_id}</td>
              <td class="px-3 py-2 text-right font-mono">{fmtCompact(a.span_count)}</td>
              <td class="px-3 py-2 text-right font-mono">{fmtCompact(a.total_input_tokens)}</td>
              <td class="px-3 py-2 text-right font-mono">{fmtCompact(a.total_output_tokens)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
