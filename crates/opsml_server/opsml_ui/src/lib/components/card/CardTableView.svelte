<script lang="ts">
  import { resolveCardPathFromArgs } from "./utils";
  import type { QueryPageResponse, CardCursor } from "$lib/components/card/types";
  import  { RegistryType } from "$lib/utils";
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';

  let { registryPage, registry, onPageChange } = $props<{
    registryPage: QueryPageResponse;
    registry: RegistryType;
    onPageChange?: (cursor: CardCursor) => Promise<void>;
  }>();

  async function handleNextPage() {
    if (registryPage.next_cursor && onPageChange) {
      await onPageChange(registryPage.next_cursor);
    }
  }

  async function handlePreviousPage() {
    if (registryPage.previous_cursor && onPageChange) {
      await onPageChange(registryPage.previous_cursor);
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
   * Get status color based on card status
   */
  function getStatusColor(status: string): string {
    switch (status) {
      case 'Ok':
        return 'bg-secondary-500';
      case 'Active':
        return 'bg-success-500';
      case 'Error':
        return 'bg-error-600';
      case 'Unset':
      default:
        return 'bg-gray-400';
    }
  }

  function getPageRange(): string {
    const offset = registryPage.page_info.offset;
    const pageSize = registryPage.page_info.page_size;
    const start = offset + 1;
    const end = offset + pageSize;
    return `${start}-${end}`;
  }

</script>

<div class="pt-4">
  <div class="overflow-x-auto border-2 border-black rounded-lg">
    <div class="h-full flex flex-col min-w-[800px]">
      <!-- Header -->
      <div class="bg-white border-b-2 border-black sticky top-0 z-10">
        <div class="grid grid-cols-[80px_200px_1fr_140px_100px] gap-2 text-black text-sm font-heading px-2 py-2">
          <div class="text-center">
            <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Id</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Date</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Space / Name</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Current Version</span>
          </div>
          <div class="text-center">
            <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Versions</span>
          </div>
        </div>
      </div>

      <!-- Rows -->
      <div class="bg-white">
        {#each registryPage.items as summary, i}
          <a
            href={resolveCardPathFromArgs(registry, summary.space, summary.name, summary.version)}
            data-sveltekit-preload-data="hover"
            class="grid grid-cols-[80px_200px_1fr_140px_100px] gap-2 items-center px-2 py-2 border-b border-gray-200 hover:bg-primary-200 cursor-pointer transition-colors no-underline {i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}"
          >
            <!-- Id (truncated uid) -->
            <div class="text-center">
              <span class="text-xs font-mono text-gray-500">{summary.uid.slice(0, 8)}</span>
            </div>

            <!-- Date with status indicator -->
            <div class="flex items-center justify-center gap-2 min-w-0">
              <div class={`w-1.5 h-4 rounded-sm flex-shrink-0 ${getStatusColor(summary.status)}`}></div>
              <span class="text-xs text-black font-mono truncate">{formatTimestamp(summary.created_at)}</span>
            </div>

            <!-- Space / Name (centered, single line) -->
            <div class="text-center min-w-0">
              <span class="text-xs text-black truncate">
                <span class="text-gray-500">{summary.space}</span>
                <span class="mx-1">/</span>
                <span class="font-medium">{summary.name}</span>
              </span>
            </div>

            <!-- Current Version -->
            <div class="text-center">
              <span class="px-1 py-1 rounded-lg bg-retro-orange-100 border-2 border-retro-orange-900 text-retro-orange-900 text-xs font-medium">
                {summary.version}
              </span>
            </div>

            <!-- Versions Count -->
            <div class="text-center">
              <span class="text-xs text-black font-medium">{summary.versions}</span>
            </div>
          </a>
        {/each}
      </div>
    </div>
  </div>

  <!-- Pagination Controls -->
  <div class="flex justify-center pt-4 gap-2 items-center">
    {#if registryPage.has_previous}
      <button
        class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
        onclick={handlePreviousPage}
        disabled={!onPageChange}
      >
        <ArrowLeft color="#5948a3"/>
      </button>
    {/if}

    <div class="flex bg-surface-50 border-black border-2 text-center items-center rounded-base px-2 shadow-small h-9">
      <span class="text-primary-800 text-xs font-medium">
        {getPageRange()}
      </span>
    </div>

    {#if registryPage.has_next}
      <button
        class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
        onclick={handleNextPage}
        disabled={!onPageChange}
      >
        <ArrowRight color="#5948a3"/>
      </button>
    {/if}
  </div>
</div>