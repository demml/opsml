<script lang="ts">
  import { AlertTriangle, Clock, Coins, Cpu, MessageSquare, Zap } from 'lucide-svelte';
  import type { AgentDashboardSummary } from './types';
  import { fmtCompact, fmtInt, fmtMs, fmtPct, fmtUsd } from './format';

  let { summary }: { summary: AgentDashboardSummary } = $props();

  const totalCost = $derived(summary.cost_by_model.reduce((a, b) => a + (b.total_cost ?? 0), 0));
  const totalTokens = $derived(summary.total_input_tokens + summary.total_output_tokens);

  const errAccent = $derived(
    summary.overall_error_rate >= 0.05
      ? { cell: 'bg-error-300', value: 'text-error-800', icon: 'text-error-800' }
      : summary.overall_error_rate > 0
        ? { cell: 'bg-error-100', value: 'text-error-700', icon: 'text-error-700' }
        : { cell: 'bg-surface-50', value: 'text-primary-950', icon: 'text-primary-700' }
  );

  type Kpi = {
    label: string;
    value: string;
    icon: typeof Zap;
    cell: string;
    value_text: string;
    icon_text: string;
  };

  const kpis = $derived<Kpi[]>([
    { label: 'Req', value: fmtCompact(summary.total_requests), icon: Zap, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'Err%', value: fmtPct(summary.overall_error_rate, 2), icon: AlertTriangle, cell: errAccent.cell, value_text: errAccent.value, icon_text: errAccent.icon },
    { label: 'p50', value: fmtMs(summary.p50_duration_ms), icon: Clock, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'p95', value: fmtMs(summary.p95_duration_ms), icon: Clock, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'p99', value: fmtMs(summary.p99_duration_ms), icon: Clock, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'Spend', value: fmtUsd(totalCost), icon: Coins, cell: 'bg-warning-100', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'Tok', value: fmtCompact(totalTokens), icon: Cpu, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'In', value: fmtCompact(summary.total_input_tokens), icon: Cpu, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'Out', value: fmtCompact(summary.total_output_tokens), icon: Cpu, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
    { label: 'Convo', value: fmtInt(summary.unique_conversation_count), icon: MessageSquare, cell: 'bg-surface-50', value_text: 'text-primary-950', icon_text: 'text-primary-700' },
  ]);
</script>

<div class="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2">
  {#each kpis as kpi (kpi.label)}
    <div class="rounded-base border-2 border-black shadow-small {kpi.cell} px-2 py-1.5">
      <div class="flex items-center gap-1 text-xs font-black uppercase tracking-widest {kpi.icon_text}">
        <kpi.icon class="w-3 h-3" /> {kpi.label}
      </div>
      <div class="text-sm font-black leading-tight {kpi.value_text}">{kpi.value}</div>
    </div>
  {/each}
</div>
