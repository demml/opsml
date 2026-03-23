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
  let isSelected = $state(false);

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

  function selectWorkflow(workflow: WorkflowWithAgent) {
    selectedWorkflow = workflow;
    isSelected = true;
  }

  function handleClosePanel() {
    selectedWorkflow = null;
    isSelected = false;
  }

  // Prompt + Nav columns added before ID; 1fr on Record UID consumes whitespace
  const gridLayout = "grid-template-columns: 120px 50px 60px 140px 100px 80px 80px 80px 100px 1fr;";
</script>

<div class="pt-2 h-full flex flex-col min-h-0 transition-opacity duration-200 {isRefreshing ? 'opacity-60 pointer-events-none' : ''}">
  <div class="border-2 border-black rounded-lg bg-white flex flex-col h-full max-h-[500px] overflow-hidden">

    <div class="overflow-auto flex-1 w-full relative">
      {#if workflows.length === 0}
        <div class="flex items-center justify-center p-8 bg-white h-full">
          <p class="text-sm font-bold text-black/50">No workflow results to display</p>
        </div>
      {:else}
        <div class="min-w-[1050px] w-full">

          <div class="bg-white border-b-2 border-black sticky top-0 z-5 w-full">
            <div class="grid gap-3 text-black text-xs font-bold px-4 py-3 items-center" style={gridLayout}>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Prompt</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Nav</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">ID</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Created</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Pass Rate</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Passed</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Failed</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Total</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Duration</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Record UID</span></div>
            </div>
          </div>

          <div class="bg-white w-full">
            {#each workflows as workflow, i}
              <button
                class="grid gap-3 items-center w-full px-4 py-3 border-b border-gray-200 transition-colors {i % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-primary-100 cursor-pointer text-left group"
                style={gridLayout}
                onclick={() => selectWorkflow(workflow)}
              >
                <div class="flex justify-center">
                  <span class="px-2 py-0.5 rounded-base border border-black bg-primary-100 text-primary-950
                               text-xss font-black uppercase tracking-wider truncate max-w-[110px]"
                        title={workflow._agentName}>
                    {workflow._agentName}
                  </span>
                </div>

                <div class="flex justify-center">
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
                </div>

                <div class="text-center">
                  <span class="text-xs font-mono text-gray-600 group-hover:text-black font-bold">{workflow.id}</span>
                </div>

                <div class="flex items-center justify-center gap-2 min-w-0">
                  <div class={`w-1.5 h-4 rounded-sm flex-shrink-0 ${passBar(workflow.pass_rate)}`}></div>
                  <span class="text-xs text-black font-mono truncate">{fmt(workflow.created_at)}</span>
                </div>

                <div class="flex justify-center">
                  <span class="px-2 py-1 rounded border-1 text-xs font-bold {passBadge(workflow.pass_rate)}">
                    {(workflow.pass_rate * 100).toFixed(1)}%
                  </span>
                </div>

                <div class="text-center">
                  <span class="text-xs font-medium text-gray-700">{workflow.passed_tasks}</span>
                </div>

                <div class="text-center">
                  <span class="text-xs font-medium text-gray-700">{workflow.failed_tasks}</span>
                </div>

                <div class="text-center">
                  <span class="text-xs font-medium text-gray-700">{workflow.total_tasks}</span>
                </div>

                <div class="text-center">
                  <span class="text-xs font-medium text-gray-700">{fmtDur(workflow.duration_ms)}</span>
                </div>

                <div class="text-center">
                  <span class="text-xs font-mono text-gray-600 group-hover:text-black font-bold">{workflow.record_uid.slice(0, 8)}</span>
                </div>
              </button>
            {/each}
          </div>

        </div>
      {/if}
    </div>

    {#if workflows.length > 0}
      <div class="border-t-2 border-black bg-gray-50 p-2 flex justify-center gap-2 items-center">
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9 px-3 flex items-center justify-center disabled:opacity-50 disabled:hover:translate-x-0 disabled:hover:translate-y-0 disabled:hover:shadow-small"
          onclick={() => onPageChange('previous')}
          disabled={!hasPrevious}
        >
          <ArrowLeft class="w-4 h-4" color="#5948a3"/>
        </button>
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9 px-3 flex items-center justify-center disabled:opacity-50 disabled:hover:translate-x-0 disabled:hover:translate-y-0 disabled:hover:shadow-small"
          onclick={() => onPageChange('next')}
          disabled={!hasNext}
        >
          <ArrowRight class="w-4 h-4" color="#5948a3"/>
        </button>
      </div>
    {/if}

  </div>

  {#if selectedWorkflow && isSelected}
    <GenAIEvalWorkflowSideBar
      selectedWorkflow={selectedWorkflow}
      profile={selectedWorkflow._profile}
      onClose={handleClosePanel}
    />
  {/if}
</div>
