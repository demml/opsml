<!--
  AgentEvalOverview.svelte
  ────────────────────────
  High-level summary cards showing the aggregate evaluation state across all
  prompt cards associated with an agent.
-->
<script lang="ts">
  import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
  import type { GenAIMonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import type { AgentPromptEvalData } from './types';
  import { CheckCircle, XCircle, AlertCircle, MessageSquareText, ListChecks } from 'lucide-svelte';

  interface Props {
    agentPromptEvals: AgentPromptEvalData[];
  }

  let { agentPromptEvals }: Props = $props();

  const successCount = $derived(agentPromptEvals.filter((e) => e.monitoringData.status === 'success').length);
  const errorCount = $derived(agentPromptEvals.filter((e) => e.monitoringData.status === 'error').length);
  const totalCount = $derived(agentPromptEvals.length);

  // Aggregate total tasks across all prompt eval profiles
  const totalTasks = $derived(
    agentPromptEvals.reduce((acc, { monitoringData }) => {
      const profile = monitoringData.profile;
      if (!profile?.tasks) return acc;
      return acc + profile.tasks.assertion.length + profile.tasks.judge.length + profile.tasks.trace.length;
    }, 0)
  );

  // Aggregate total records from successful dashboards
  const totalRecords = $derived(
    agentPromptEvals.reduce((acc, { monitoringData }) => {
      if (monitoringData.status !== 'success') return acc;
      return acc + (monitoringData.selectedData.records?.items?.length ?? 0);
    }, 0)
  );

  const summaryCards = $derived([
    {
      label: 'Prompt Cards',
      value: totalCount,
      icon: MessageSquareText,
      bg: 'bg-primary-100',
      border: 'border-primary-800',
      text: 'text-primary-900',
    },
    {
      label: 'Active Evals',
      value: successCount,
      icon: CheckCircle,
      bg: 'bg-green-100',
      border: 'border-green-700',
      text: 'text-green-900',
    },
    {
      label: 'Unavailable',
      value: errorCount,
      icon: XCircle,
      bg: 'bg-warning-100',
      border: 'border-warning-700',
      text: 'text-warning-900',
    },
    {
      label: 'Total Tasks',
      value: totalTasks,
      icon: ListChecks,
      bg: 'bg-secondary-100',
      border: 'border-secondary-800',
      text: 'text-secondary-900',
    },
    {
      label: 'Recent Records',
      value: totalRecords,
      icon: AlertCircle,
      bg: 'bg-surface-100',
      border: 'border-black',
      text: 'text-black',
    },
  ]);
</script>

<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
  {#each summaryCards as card}
    {@const Icon = card.icon}
    <div class="rounded-base border-2 {card.border} {card.bg} shadow-small p-4 flex flex-col gap-2">
      <div class="flex items-center justify-between">
        <span class="text-xs font-black uppercase tracking-wide text-slate-600">{card.label}</span>
        <Icon class="w-4 h-4 {card.text}" />
      </div>
      <span class="text-3xl font-black {card.text}">{card.value}</span>
    </div>
  {/each}
</div>
