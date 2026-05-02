<script lang="ts">
  import { AlertTriangle, Clock, Coins, Cpu, MessageSquare, Zap } from 'lucide-svelte';
  import type { AgentDashboardSummary } from './types';
  import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from './format';

  let { summary }: { summary: AgentDashboardSummary } = $props();

  const totalCost = $derived(summary.cost_by_model.reduce((a, b) => a + (b.total_cost ?? 0), 0));
  const totalTokens = $derived(summary.total_input_tokens + summary.total_output_tokens);

  const kpis = $derived([
    { label: 'Req', value: fmtCompact(summary.total_requests), icon: Zap, accent: 'bg-surface-50' },
    { label: 'Err%', value: fmtPct(summary.overall_error_rate, 2), icon: AlertTriangle, accent: summary.overall_error_rate > 0.02 ? 'bg-error-100' : 'bg-surface-50' },
    { label: 'p50', value: fmtMs(summary.p50_duration_ms), icon: Clock, accent: 'bg-surface-50' },
    { label: 'p95', value: fmtMs(summary.p95_duration_ms), icon: Clock, accent: 'bg-surface-50' },
    { label: 'p99', value: fmtMs(summary.p99_duration_ms), icon: Clock, accent: 'bg-surface-50' },
    { label: 'Spend', value: fmtUsd(totalCost), icon: Coins, accent: 'bg-warning-100' },
    { label: 'Tok', value: fmtCompact(totalTokens), icon: Cpu, accent: 'bg-surface-50' },
    { label: 'In', value: fmtCompact(summary.total_input_tokens), icon: Cpu, accent: 'bg-surface-50' },
    { label: 'Out', value: fmtCompact(summary.total_output_tokens), icon: Cpu, accent: 'bg-surface-50' },
    { label: 'Convo', value: fmtInt(summary.unique_conversation_count), icon: MessageSquare, accent: 'bg-surface-50' },
  ]);
</script>

<div class="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2">
  {#each kpis as kpi (kpi.label)}
    <div class="rounded-base border-2 border-black shadow-small {kpi.accent} px-2 py-1.5">
      <div class="flex items-center gap-1 text-xs font-black text-primary-700 uppercase tracking-widest">
        <kpi.icon class="w-3 h-3" /> {kpi.label}
      </div>
      <div class="text-sm font-black text-primary-950 leading-tight">{kpi.value}</div>
    </div>
  {/each}
</div>
