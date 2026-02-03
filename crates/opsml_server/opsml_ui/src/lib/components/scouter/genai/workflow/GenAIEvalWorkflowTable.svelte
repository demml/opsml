<script lang="ts">
  import type { GenAIEvalWorkflowResult } from '../task';
  import type { GenAIEvalProfile, GenAIEvalWorkflowPaginationResponse } from '../types';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';
  import GenAIEvalWorkflowSideBar from './GenAIEvalWorkflowSideBar.svelte';

  let {
    currentPage,
    onPageChange,
    profile
  } = $props<{
    currentPage: GenAIEvalWorkflowPaginationResponse;
    onPageChange: (cursor: RecordCursor, direction: string) => void;
    profile: GenAIEvalProfile;
  }>();

  let workflows = $state<GenAIEvalWorkflowResult[]>(currentPage.items || []);
  let selectedWorkflow = $state<GenAIEvalWorkflowResult | null>(null);
  let isSelected = $state(false);

  // Sync state
  $effect(() => {
    workflows = currentPage.items || [];
  });

  async function handleNextPage() {
    if (currentPage.has_next && currentPage.next_cursor && onPageChange) {
      await onPageChange(currentPage.next_cursor, 'next');
    }
  }

  async function handlePreviousPage() {
    if (currentPage.has_previous && currentPage.previous_cursor && onPageChange) {
      await onPageChange(currentPage.previous_cursor, 'previous');
    }
  }

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  }

  function getPassRateBadge(passRate: number): string {
    if (passRate >= 0.9) return 'bg-secondary-100 border-secondary-900 text-secondary-900';
    if (passRate >= 0.7) return 'bg-warning-100 border-warning-900 text-warning-900';
    return 'bg-error-100 border-error-900 text-error-900';
  }

  function getPassRateColor(passRate: number): string {
    if (passRate >= 0.9) return 'bg-secondary-600';
    if (passRate >= 0.7) return 'bg-warning-600';
    return 'bg-error-600';
  }

  function formatDuration(durationMs: number): string {
    const seconds = durationMs / 1000;
    return seconds < 1 ? `${durationMs}ms` : `${seconds.toFixed(2)}s`;
  }

  function selectWorkflowForDetail(workflow: GenAIEvalWorkflowResult) {
    selectedWorkflow = workflow;
    isSelected = true;
  }

  function handleClosePanel() {
    selectedWorkflow = null;
    isSelected = false;
  }

  // --- GRID FIX ---
  // Matches Record Table logic: 1fr on the last column (Record UID) to consume whitespace.
  const gridLayout = "grid-template-columns: 60px 140px 100px 80px 80px 80px 100px 1fr;";
</script>

<div class="pt-2 h-full flex flex-col min-h-0">
  <div class="border-2 border-black rounded-lg bg-white flex flex-col h-full max-h-[500px] overflow-hidden">

    <div class="overflow-auto flex-1 w-full relative">
      {#if workflows.length === 0}
        <div class="flex items-center justify-center p-8 bg-white h-full">
          <p class="text-sm font-bold text-gray-500">No workflow results to display</p>
        </div>
      {:else}
        <div class="min-w-[900px] w-full">

            <div class="bg-white border-b-2 border-black sticky top-0 z-20 w-full">
              <div class="grid gap-3 text-black text-xs font-bold px-4 py-3 items-center" style={gridLayout}>
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
                  onclick={() => selectWorkflowForDetail(workflow)}
                >
                  <div class="text-center">
                    <span class="text-xs font-mono text-gray-600 group-hover:text-black font-bold">{workflow.id}</span>
                  </div>

                  <div class="flex items-center justify-center gap-2 min-w-0">
                    <div class={`w-1.5 h-4 rounded-sm flex-shrink-0 ${getPassRateColor(workflow.pass_rate)}`}></div>
                    <span class="text-xs text-black font-mono truncate">
                      {formatTimestamp(workflow.created_at)}
                    </span>
                  </div>

                  <div class="flex justify-center">
                    <span class="px-2 py-1 rounded border-1 text-xs font-bold {getPassRateBadge(workflow.pass_rate)}">
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
                    <span class="text-xs font-medium text-gray-700">{formatDuration(workflow.duration_ms)}</span>
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
          onclick={handlePreviousPage}
          disabled={!currentPage.has_previous}
        >
          <ArrowLeft class="w-4 h-4" color="#5948a3"/>
        </button>

        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9 px-3 flex items-center justify-center disabled:opacity-50 disabled:hover:translate-x-0 disabled:hover:translate-y-0 disabled:hover:shadow-small"
          onclick={handleNextPage}
          disabled={!currentPage.has_next}
        >
          <ArrowRight class="w-4 h-4" color="#5948a3"/>
        </button>
      </div>
    {/if}

  </div>

  {#if selectedWorkflow && isSelected}
    <GenAIEvalWorkflowSideBar selectedWorkflow={selectedWorkflow} onClose={handleClosePanel} profile={profile} />
  {/if}
</div>