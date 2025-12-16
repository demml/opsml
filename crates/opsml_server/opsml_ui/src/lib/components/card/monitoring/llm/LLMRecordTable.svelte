<script lang="ts">
  import type { LLMDriftServerRecord, LLMDriftRecordPaginationResponse } from "./llm";
  import type { RecordCursor } from "../types";
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";

  let {
    currentPage,
    onPageChange
  } = $props<{
    currentPage: LLMDriftRecordPaginationResponse;
    onPageChange: (cursor: RecordCursor, direction: string) => void;
  }>();

  let records = $state<LLMDriftServerRecord[]>(currentPage.items || []);

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

  /**
   * Format timestamp for display
   */
  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  }

  /**
   * Get status badge styling
   */
  function getStatusBadge(status: string): string {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-warning-100 border-warning-900 text-warning-900';
      case 'processing':
        return 'bg-tertiary-100 border-tertiary-900 text-tertiary-900';
      case 'processed':
        return 'bg-success-100 border-success-900 text-success-900';
      case 'failed':
        return 'bg-error-100 border-error-900 text-error-900';
      default:
        return 'bg-primary-100 border-primary-900 text-primary-900';
    }
  }

  /**
   * Format processing duration for display
   */
  function formatDuration(duration?: number): string {
    if (duration === undefined) return 'N/A';
    const seconds = duration / 1000;
    return seconds < 1 ? `${duration}ms` : `${seconds.toFixed(2)}s`;
  }
</script>

<div class="pt-4">
  <!-- Header with title -->
  <div class="mb-4">
    <h2 class="text-lg font-bold text-primary-800">LLM Drift Records</h2>
  </div>

  <!-- Table Container -->
  <div class="overflow-x-auto border-2 border-black rounded-lg">
    <div class="h-full flex flex-col min-w-[1000px]">
      {#if records.length === 0}
        <!-- Empty State -->
        <div class="flex items-center justify-center p-12 bg-white">
          <p class="text-lg font-bold text-gray-500">No LLM drift records to display</p>
        </div>
      {:else}
        <!-- Header -->
        <div class="bg-white border-b-2 border-black sticky top-0 z-10">
          <div class="grid grid-cols-[80px_120px_100px_100px_100px_140px_120px] gap-2 text-black text-sm font-heading px-2 py-2">
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">ID</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Status</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Score</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Prompt</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Context</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Created</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Duration</span>
            </div>
          </div>
        </div>

        <!-- Rows -->
        <div class="bg-white">
          {#each records as record, i}
            <div
              class="grid grid-cols-[80px_120px_100px_100px_100px_140px_120px] gap-2 items-center px-2 py-2 border-b border-gray-200 transition-colors {i % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-primary-200"
            >
              <!-- ID -->
              <div class="text-center">
                <span class="text-xs font-mono text-gray-500">{record.id}</span>
              </div>

              <!-- Status Badge -->
              <div class="text-center">
                <span class="px-2 py-1 rounded-lg border-2 text-xs font-medium {getStatusBadge(record.status)}">
                  {record.status.toUpperCase()}
                </span>
              </div>

              <!-- Score Modal -->
              <div class="flex justify-center">
                <CodeModal name='Score' code={JSON.stringify(record.score, null, 2)} />
              </div>

              <!-- Prompt Modal -->
              <div class="flex justify-center">
                {#if record.prompt}
                  <CodeModal name='Prompt' code={record.prompt} />
                {:else}
                  <span class="text-xs text-gray-400">—</span>
                {/if}
              </div>

              <!-- Context Modal -->
              <div class="flex justify-center">
                {#if record.context}
                  <CodeModal name='Context' code={record.context} />
                {:else}
                  <span class="text-xs text-gray-400">—</span>
                {/if}
              </div>

              <!-- Created Date -->
              <div class="text-center">
                <span class="text-xs text-black font-mono">
                  {formatTimestamp(record.created_at)}
                </span>
              </div>

              <!-- Processing Duration -->
              <div class="text-center">
                <span class="px-2 py-1 rounded-lg border-2 border-black bg-surface-100 text-xs font-medium">
                  {formatDuration(record.processing_duration)}
                </span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Pagination Controls -->
  {#if records.length > 0}
    <div class="flex justify-center pt-4 gap-2 items-center">
      {#if currentPage.has_previous}
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
          onclick={handlePreviousPage}
        >
          <ArrowLeft color="#5948a3"/>
        </button>
      {/if}

      {#if currentPage.has_next}
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
          onclick={handleNextPage}
        >
          <ArrowRight color="#5948a3"/>
        </button>
      {/if}
    </div>
  {/if}
</div>