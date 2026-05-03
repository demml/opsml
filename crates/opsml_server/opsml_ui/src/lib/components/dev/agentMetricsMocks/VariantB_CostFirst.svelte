<script lang="ts">
  import {
    AlertTriangle,
    Clock,
    Coins,
    Cpu,
    Flame,
    TrendingDown,
    TrendingUp,
    Wrench,
    Zap,
    ChevronDown
  } from 'lucide-svelte';
  import ChartCard from '$lib/components/card/agent/observability/GenAiChartCard.svelte';
  import {
    buildCostChart,
    buildCostDonut,
    buildTokenChart,
    buildLatencyChart,
    buildToolStackChart
  } from './charts';
  import type { MockMetricsBundle } from './types';
  import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from './format';

  let { bundle }: { bundle: MockMetricsBundle } = $props();

  const summary = $derived(bundle.agent_dashboard.summary);
  const totalCost = $derived(
    summary.cost_by_model.reduce((a, b) => a + (b.total_cost ?? 0), 0)
  );
  const projectedDaily = $derived(totalCost * 24);
  const projectedMonthly = $derived(projectedDaily * 30);
  const costPerRequest = $derived(
    summary.total_requests > 0 ? totalCost / summary.total_requests : 0
  );
  const costPer1kTokens = $derived(
    summary.total_input_tokens + summary.total_output_tokens > 0
      ? (totalCost / (summary.total_input_tokens + summary.total_output_tokens)) * 1000
      : 0
  );

  const sortedModels = $derived(
    [...summary.cost_by_model].sort((a, b) => (b.total_cost ?? 0) - (a.total_cost ?? 0))
  );
  const topModel = $derived(sortedModels[0]);
  const topModelShare = $derived(
    topModel ? ((topModel.total_cost ?? 0) / totalCost) * 100 : 0
  );
</script>

<div class="space-y-5">
  <!-- Hero: Spend snapshot -->
  <div class="rounded-base border-2 border-black shadow bg-gradient-to-br from-warning-200 to-warning-100 p-5">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-warning-900">
          <Flame class="w-4 h-4" /> Spend · Past 1 Hour
        </div>
        <div class="text-5xl font-black text-black mt-2">{fmtUsd(totalCost)}</div>
        <div class="flex items-center gap-2 text-xs font-mono text-black/70 mt-1">
          <TrendingUp class="w-3.5 h-3.5 text-success-700" />
          <span>+12.3% vs prior hour</span>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="flex items-center gap-2 px-3 py-1.5 bg-surface-50 border-2 border-black rounded-base shadow-small text-xs font-bold">
          <Clock class="w-3.5 h-3.5" /> Past 1 Hour <ChevronDown class="w-3 h-3" />
        </button>
        <button class="flex items-center gap-2 px-3 py-1.5 bg-surface-50 border-2 border-black rounded-base shadow-small text-xs font-bold">
          Service: research-agent <ChevronDown class="w-3 h-3" />
        </button>
      </div>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
      <div class="rounded-base border-2 border-black bg-surface-50 p-3">
        <div class="text-[10px] font-black text-primary-700 uppercase tracking-widest">Cost / Req</div>
        <div class="text-xl font-black text-black mt-0.5">{fmtUsd(costPerRequest)}</div>
      </div>
      <div class="rounded-base border-2 border-black bg-surface-50 p-3">
        <div class="text-[10px] font-black text-primary-700 uppercase tracking-widest">Cost / 1k tok</div>
        <div class="text-xl font-black text-black mt-0.5">{fmtUsd(costPer1kTokens)}</div>
      </div>
      <div class="rounded-base border-2 border-black bg-surface-50 p-3">
        <div class="text-[10px] font-black text-primary-700 uppercase tracking-widest">Proj. Daily</div>
        <div class="text-xl font-black text-black mt-0.5">{fmtUsd(projectedDaily)}</div>
      </div>
      <div class="rounded-base border-2 border-black bg-surface-50 p-3">
        <div class="text-[10px] font-black text-primary-700 uppercase tracking-widest">Proj. Monthly</div>
        <div class="text-xl font-black text-black mt-0.5">{fmtUsd(projectedMonthly)}</div>
      </div>
    </div>
  </div>

  <!-- Cost time series + donut -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
    <div class="lg:col-span-2">
      <ChartCard
        title="Spend Over Time"
        subtitle="$ per bucket"
        configFn={() => buildCostChart(bundle.agent_dashboard.buckets)}
      />
    </div>
    <ChartCard
      title="Spend by Model"
      subtitle="window total"
      configFn={() => buildCostDonut(summary.cost_by_model)}
    />
  </div>

  <!-- Top spend leaderboard -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
    <div class="px-4 py-2.5 border-b-2 border-black bg-surface-100 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Coins class="w-4 h-4 text-warning-700" />
        <span class="text-sm font-black uppercase tracking-wide text-primary-800">Spend Leaderboard</span>
      </div>
      {#if topModel}
        <span class="text-xs font-mono text-gray-700">
          top: <span class="font-bold text-primary-900">{topModel.model}</span> · {topModelShare.toFixed(1)}%
        </span>
      {/if}
    </div>
    <div class="divide-y-2 divide-black">
      {#each sortedModels as m, i}
        {@const share = ((m.total_cost ?? 0) / totalCost) * 100}
        <div class="p-3 grid grid-cols-12 gap-3 items-center hover:bg-primary-50">
          <div class="col-span-1 text-2xl font-black text-primary-700">#{i + 1}</div>
          <div class="col-span-3">
            <div class="font-mono font-bold text-primary-900">{m.model}</div>
            <div class="text-[10px] font-mono text-gray-700">
              {fmtCompact(m.total_input_tokens)} in · {fmtCompact(m.total_output_tokens)} out
            </div>
          </div>
          <div class="col-span-6">
            <div class="h-5 bg-surface-100 border-2 border-black rounded-base overflow-hidden">
              <div class="h-full bg-warning-300 border-r-2 border-black flex items-center justify-end pr-2"
                   style="width: {share}%">
                <span class="text-[10px] font-black text-black">{share.toFixed(1)}%</span>
              </div>
            </div>
          </div>
          <div class="col-span-2 text-right">
            <div class="text-lg font-black text-black">{fmtUsd(m.total_cost ?? 0)}</div>
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Volume side metrics -->
  <div class="grid grid-cols-1 lg:grid-cols-4 gap-3">
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-primary-700 uppercase tracking-wider">
        <Zap class="w-3.5 h-3.5" /> Requests
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtCompact(summary.total_requests)}</div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-primary-700 uppercase tracking-wider">
        <Cpu class="w-3.5 h-3.5" /> Tokens
      </div>
      <div class="text-2xl font-black text-black mt-1">
        {fmtCompact(summary.total_input_tokens + summary.total_output_tokens)}
      </div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-surface-50 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-primary-700 uppercase tracking-wider">
        <Clock class="w-3.5 h-3.5" /> p95 Latency
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtMs(summary.p95_duration_ms)}</div>
    </div>
    <div class="rounded-base border-2 border-black shadow-small bg-error-100 p-3">
      <div class="flex items-center gap-1.5 text-xs font-black text-error-900 uppercase tracking-wider">
        <AlertTriangle class="w-3.5 h-3.5" /> Error Rate
      </div>
      <div class="text-2xl font-black text-black mt-1">{fmtPct(summary.overall_error_rate, 2)}</div>
    </div>
  </div>

  <!-- Token + latency context -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
    <ChartCard
      title="Token Mix"
      subtitle="input · output · cache_read"
      configFn={() => buildTokenChart(bundle.agent_dashboard.buckets)}
    />
    <ChartCard
      title="Latency"
      subtitle="p50 · p95 · p99"
      configFn={() => buildLatencyChart(bundle.agent_dashboard.buckets)}
    />
  </div>

  <!-- Tool spend impact -->
  <ChartCard
    title="Tool Calls Over Time"
    subtitle="stacked by tool"
    configFn={() => buildToolStackChart(bundle.tool_dashboard.time_series)}
    height="h-72"
  />

  <!-- Cost-saving opportunities -->
  <div class="rounded-base border-2 border-black shadow bg-success-100 p-4">
    <div class="flex items-center gap-2 text-sm font-black uppercase tracking-wide text-success-900">
      <TrendingDown class="w-4 h-4" /> Optimization Hints
    </div>
    <ul class="mt-2 space-y-1.5 text-sm text-black">
      <li class="font-mono">
        <span class="font-bold">·</span> Cache read tokens: {fmtCompact(summary.total_cache_read_tokens)} —
        good cache utilization
      </li>
      <li class="font-mono">
        <span class="font-bold">·</span> Top model {topModel?.model ?? '—'} drives {topModelShare.toFixed(1)}% of spend.
        Consider routing simpler queries to a smaller model.
      </li>
      <li class="font-mono">
        <span class="font-bold">·</span> Cost per request: {fmtUsd(costPerRequest)} — flag conversations &gt; $0.10.
      </li>
    </ul>
  </div>
</div>
