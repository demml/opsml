<script lang="ts">
  import type { GenAIEvalWorkflowResult} from '../task';
  import type { GenAIEvalWorkflowPaginationResponse } from '../types';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';
  import GenAIEvalWorkflowSideBar from './GenAIEvalWorkflowSideBar.svelte';

  let {
    currentPage,
    onPageChange
  } = $props<{
    currentPage: GenAIEvalWorkflowPaginationResponse;
    onPageChange: (cursor: RecordCursor, direction: string) => void;
  }>();

  let workflows = $state<GenAIEvalWorkflowResult[]>(currentPage.items || []);
  let selectedWorkflow = $state<GenAIEvalWorkflowResult | null>(null);
  let isSelected = $state(false);

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
    if (passRate >= 0.9) return 'bg-success-100 border-success-900 text-success-900';
    if (passRate >= 0.7) return 'bg-warning-100 border-warning-900 text-warning-900';
    return 'bg-error-100 border-error-900 text-error-900';
  }

  function getPassRateColor(passRate: number): string {
    if (passRate >= 0.9) return 'bg-success-600';
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
</script>

<div class="pt-4">
  <div class="mb-3">
    <h2 class="text-base font-bold text-primary-800">GenAI Evaluation Workflows</h2>
  </div>

  <div class="overflow-hidden border-2 border-black rounded-lg max-h-[500px] flex flex-col">
    <div class="overflow-y-auto flex-1">
      {#if workflows.length === 0}
        <div class="flex items-center justify-center p-8 bg-white">
          <p class="text-sm font-bold text-gray-500">No workflow results to display</p>
        </div>
      {:else}
        <div class="bg-white border-b-2 border-black sticky top-0 z-10">
          <div class="grid grid-cols-6 gap-3 text-black text-xs font-bold px-4 py-3" style="grid-template-columns: 80px 140px 120px 100px 120px 1fr;">
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">ID</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Created</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Pass Rate</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Tasks</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Duration</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Record UID</span>
            </div>
          </div>
        </div>

        <div class="bg-white">
          {#each workflows as workflow, i}
            <button
              class="grid gap-3 items-center w-full px-4 py-3 border-b border-gray-200 transition-colors {i % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-primary-100 cursor-pointer text-left"
              style="grid-template-columns: 80px 140px 120px 100px 120px 1fr;"
              onclick={() => selectWorkflowForDetail(workflow)}
            >
              <div class="text-center">
                <span class="text-xs font-mono text-gray-600">{workflow.id}</span>
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
                <span class="text-xs font-medium text-gray-700">
                  {workflow.passed_tasks}/{workflow.total_tasks}
                </span>
              </div>

              <div class="text-center">
                <span class="text-xs font-medium text-gray-700">
                  {formatDuration(workflow.duration_ms)}
                </span>
              </div>

              <div class="text-center">
                <span class="text-xs font-mono text-gray-600 truncate">
                  {workflow.record_uid.slice(0, 16)}...
                </span>
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  {#if selectedWorkflow && isSelected}
    <GenAIEvalWorkflowSideBar
      {selectedWorkflow}
      onClose={handleClosePanel}
    />
  {/if}

  {#if workflows.length > 0}
    <div class="flex justify-center pt-4 gap-2 items-center">
      {#if currentPage.has_previous}
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
          onclick={handlePreviousPage}
        >
          <ArrowLeft class="w-4 h-4" color="#5948a3"/>
        </button>
      {/if}

      {#if currentPage.has_next}
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
          onclick={handleNextPage}
        >
          <ArrowRight class="w-4 h-4" color="#5948a3"/>
        </button>
      {/if}
    </div>
  {/if}
</div>