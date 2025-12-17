<script lang="ts">
  import type { LLMDriftServerRecord, LLMDriftRecordPaginationResponse } from "./llm";
  import type { RecordCursor } from "../types";
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';
  import LLMRecordSideBar from "./LLMRecordSideBar.svelte";

  let {
    currentPage,
    onPageChange
  } = $props<{
    currentPage: LLMDriftRecordPaginationResponse;
    onPageChange: (cursor: RecordCursor, direction: string) => void;
  }>();

  let records = $state<LLMDriftServerRecord[]>(currentPage.items || []);
  let selectedRecord = $state<LLMDriftServerRecord | null>(null);
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

  function getStatusBadge(status: string): string {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-warning-100 border-warning-900 text-warning-900';
      case 'processing':
        return 'bg-primary-100 border-primary-900 text-primary-900';
      case 'processed':
        return 'bg-secondary-100 border-secondary-900 text-secondary-900';
      case 'failed':
        return 'bg-error-100 border-error-900 text-error-900';
      default:
        return 'bg-primary-100 border-primary-900 text-primary-900';
    }
  }

  function getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'processed':
        return 'bg-secondary-600';
      case 'processing':
        return 'bg-primary-600';
      case 'pending':
        return 'bg-warning-600';
      case 'failed':
        return 'bg-error-600';
      default:
        return 'bg-gray-400';
    }
  }

  function formatDuration(duration?: number): string {
    if (duration === undefined) return 'N/A';
    const seconds = duration / 1000;
    return seconds < 1 ? `${duration}ms` : `${seconds.toFixed(2)}s`;
  }

  function selectRecordForDetail(record: LLMDriftServerRecord) {
    selectedRecord = record;
    isSelected = true;
  }

  function handleClosePanel() {
    selectedRecord = null;
    isSelected = false;
  }

  function hasScoreData(record: LLMDriftServerRecord): boolean {
    return record.score && Object.keys(record.score).length > 0;
  }
</script>

<div class="pt-4">
  <!-- Header with title -->
  <div class="mb-3">
    <h2 class="text-base font-bold text-primary-800">LLM Drift Records</h2>
  </div>

  <!-- Table Container -->
  <div class="overflow-hidden border-2 border-black rounded-lg max-h-[500px] flex flex-col">
    <div class="overflow-y-auto flex-1">
      {#if records.length === 0}
        <!-- Empty State -->
        <div class="flex items-center justify-center p-8 bg-white">
          <p class="text-sm font-bold text-gray-500">No LLM drift records to display</p>
        </div>
      {:else}
        <!-- Header -->
        <div class="bg-white border-b-2 border-black sticky top-0 z-10">
          <div class="grid grid-cols-5 gap-3 text-black text-xs font-bold px-4 py-3" style="grid-template-columns: 80px 140px 100px 1fr 120px;">
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">ID</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Created</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Status</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Has Score</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Duration</span>
            </div>
          </div>
        </div>

        <!-- Rows -->
        <div class="bg-white">
          {#each records as record, i}
            <button
              class="grid gap-3 items-center w-full px-4 py-3 border-b border-gray-200 transition-colors {i % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-primary-100 cursor-pointer text-left"
              style="grid-template-columns: 80px 140px 100px 1fr 120px;"
              onclick={() => selectRecordForDetail(record)}
            >
              <!-- ID (truncated uid) -->
              <div class="text-center">
                <span class="text-xs font-mono text-gray-600">{record.uid.slice(0, 8)}</span>
              </div>

              <!-- Created Date with status indicator -->
              <div class="flex items-center justify-center gap-2 min-w-0">
                <div class={`w-1.5 h-4 rounded-sm flex-shrink-0 ${getStatusColor(record.status)}`}></div>
                <span class="text-xs text-black font-mono truncate">
                  {formatTimestamp(record.created_at)}
                </span>
              </div>

              <!-- Status Badge -->
              <div class="flex justify-center">
                <span class="px-2 py-1 rounded border-1 text-xs font-bold {getStatusBadge(record.status)}">
                  {record.status.toUpperCase()}
                </span>
              </div>

              <!-- Has Score -->
              <div class="text-center">
                {#if hasScoreData(record)}
                  <span class="px-2 py-1 rounded border-1 bg-success-100 border-success-900 text-success-900 text-xs font-bold">
                    Yes
                  </span>
                {:else}
                  <span class="px-2 py-1 rounded border-1 bg-gray-100 border-gray-400 text-gray-600 text-xs font-bold">
                    No
                  </span>
                {/if}
              </div>

              <!-- Processing Duration -->
              <div class="text-center">
                <span class="text-xs font-medium text-gray-700">
                  {formatDuration(record.processing_duration)}
                </span>
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  {#if selectedRecord && isSelected}
    <LLMRecordSideBar
      selectedRecord={selectedRecord}
      onClose={handleClosePanel}
    />
  {/if}

  <!-- Pagination Controls -->
  {#if records.length > 0}
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