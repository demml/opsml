<!--
  AgentEvalWorkflowTable.svelte
  ─────────────────────────────
  Displays merged workflow results from all agent-associated prompt cards.
  Receives a flat sorted list + pagination booleans from AgentEvalDashboard.
  Manages its own row-detail sidebar.
-->
<script lang="ts">
  import type { WorkflowWithAgent } from './types';
  import { ArrowLeft, ArrowRight, ExternalLink } from 'lucide-svelte';
  import GenAIEvalWorkflowSideBar from '$lib/components/scouter/genai/workflow/GenAIEvalWorkflowSideBar.svelte';

  let {
    workflows,
    hasNext,
    hasPrevious,
    onPageChange,
    isRefreshing = false,
  }: {
    workflows: WorkflowWithAgent[];
    hasNext: boolean;
    hasPrevious: boolean;
    onPageChange: (direction: string) => void;
    isRefreshing?: boolean;
  } = $props();

  let selectedWorkflow = $state<WorkflowWithAgent | null>(null);

  function fmt(ts: string): string {
    return new Date(ts).toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true,
    });
  }

  function fmtDur(ms: number): string {
    const s = ms / 1000;
    return s < 1 ? `${ms}ms` : `${s.toFixed(2)}s`;
  }

  function passBadge(rate: number): string {
    if (rate >= 0.9) return 'bg-secondary-100 border-secondary-900 text-secondary-900';
    if (rate >= 0.7) return 'bg-warning-100 border-warning-900 text-warning-900';
    return 'bg-error-100 border-error-900 text-error-900';
  }

  function passBar(rate: number): string {
    if (rate >= 0.9) return 'bg-secondary-600';
    if (rate >= 0.7) return 'bg-warning-600';
    return 'bg-error-600';
  }

  const thClass = 'px-3 py-2 text-center text-xss font-black uppercase tracking-wider text-primary-700 whitespace-nowrap';
  const tdClass = 'px-3 py-2.5 text-center align-middle';
</script>

<div class="overflow-auto max-h-[500px] transition-opacity duration-200 {isRefreshing ? 'opacity-60 pointer-events-none' : ''}">
  {#if workflows.length === 0}
    <div class="flex items-center justify-center py-12">
      <p class="text-sm font-bold text-black/50">No workflow results to display</p>
    </div>
  {:else}
    <table class="min-w-max w-full text-sm border-collapse">
      <thead class="bg-surface-200 border-b-2 border-black sticky top-0 z-10">
        <tr>
          <th class={thClass}>Prompt</th>
          <th class={thClass}>Nav</th>
          <th class={thClass}>ID</th>
          <th class={thClass}>Created</th>
          <th class={thClass}>Pass Rate</th>
          <th class={thClass}>Passed</th>
          <th class={thClass}>Failed</th>
          <th class={thClass}>Total</th>
          <th class={thClass}>Duration</th>
          <th class={thClass}>Record UID</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-black/10">
        {#each workflows as workflow, i}
          <tr
            class="cursor-pointer transition-colors duration-100 group
                   {i % 2 === 0 ? 'bg-surface-50' : 'bg-surface-100'} hover:bg-primary-50"
            onclick={() => { selectedWorkflow = workflow; }}
          >
            <td class={tdClass}>
              <span class="px-2 py-0.5 rounded-base border border-black bg-primary-100 text-primary-950
                           text-xss font-black uppercase tracking-wider inline-block max-w-[110px] truncate"
                    title={workflow._agentName}>
                {workflow._agentName}
              </span>
            </td>
            <td class={tdClass}>
              <a
                href={workflow._evalPath}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Open prompt evaluation page"
                class="p-1.5 rounded-base border-2 border-black bg-surface-50
                       hover:bg-primary-100 shadow-small shadow-hover-small
                       transition-transform duration-100 inline-flex items-center justify-center"
                onclick={(e) => e.stopPropagation()}
              >
                <ExternalLink class="w-3 h-3 text-primary-700" />
              </a>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black/60 group-hover:text-black font-bold">{workflow.id}</span>
            </td>
            <td class={tdClass}>
              <div class="flex items-center justify-center gap-1.5">
                <div class="w-1.5 h-4 rounded-sm flex-shrink-0 {passBar(workflow.pass_rate)}"></div>
                <span class="text-xs text-black font-mono whitespace-nowrap">{fmt(workflow.created_at)}</span>
              </div>
            </td>
            <td class={tdClass}>
              <span class="px-2 py-0.5 rounded-base border text-xss font-black {passBadge(workflow.pass_rate)}">
                {(workflow.pass_rate * 100).toFixed(1)}%
              </span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black">{workflow.passed_tasks}</span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black">{workflow.failed_tasks}</span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black">{workflow.total_tasks}</span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black whitespace-nowrap">{fmtDur(workflow.duration_ms)}</span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black/60 group-hover:text-black font-bold">
                {workflow.record_uid.slice(0, 8)}
              </span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

{#if workflows.length > 0}
  <div class="border-t-2 border-black bg-surface-200 p-2 flex justify-center gap-2 items-center">
    <button
      class="btn bg-surface-50 border-black border-2 shadow-small shadow-click-small h-9 px-3
             flex items-center justify-center transition-transform duration-100 ease-out
             disabled:opacity-40 disabled:pointer-events-none"
      onclick={() => onPageChange('previous')}
      disabled={!hasPrevious}
    >
      <ArrowLeft class="w-4 h-4 text-primary-700" />
    </button>
    <button
      class="btn bg-surface-50 border-black border-2 shadow-small shadow-click-small h-9 px-3
             flex items-center justify-center transition-transform duration-100 ease-out
             disabled:opacity-40 disabled:pointer-events-none"
      onclick={() => onPageChange('next')}
      disabled={!hasNext}
    >
      <ArrowRight class="w-4 h-4 text-primary-700" />
    </button>
  </div>
{/if}

{#if selectedWorkflow}
  <GenAIEvalWorkflowSideBar
    selectedWorkflow={selectedWorkflow}
    profile={selectedWorkflow._profile}
    onClose={() => { selectedWorkflow = null; }}
  />
{/if}
