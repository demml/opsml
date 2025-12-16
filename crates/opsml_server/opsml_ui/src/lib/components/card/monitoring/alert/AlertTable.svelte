<script lang="ts">
  import type { Alert, DriftAlertPaginationResponse } from "./types";
  import CodeModal from "../CodeModal.svelte";
  import type { RecordCursor } from "../types";
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';

  let {
    driftAlerts,
    updateAlert,
    onPageChange
  } = $props<{
    driftAlerts: DriftAlertPaginationResponse;
    updateAlert: (id: number, space: string) => Promise<void>;
    onPageChange: (cursor: RecordCursor, direction: string) => void;
  }>();

  let alerts = $state<Alert[]>(driftAlerts.items || []);

  async function handleNextPage() {
    if (driftAlerts.has_next && driftAlerts.next_cursor && onPageChange) {
      await onPageChange(driftAlerts.next_cursor, 'next');
    }
  }

  async function handlePreviousPage() {
    if (driftAlerts.has_previous && driftAlerts.previous_cursor && onPageChange) {
      await onPageChange(driftAlerts.previous_cursor, 'previous');
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
   * Get drift type badge styling
   */
  function getDriftTypeBadge(driftType: string): string {
    switch (driftType) {
      case 'spc':
        return 'bg-warning-100 border-warning-900 text-warning-900';
      case 'psi':
        return 'bg-tertiary-100 border-tertiary-900 text-tertiary-900';
      case 'custom':
        return 'bg-success-100 border-success-900 text-success-900';
      default:
        return 'bg-primary-100 border-primary-900 text-primary-900';
    }
  }


</script>

<div class="pt-4">
  <!-- Header with title -->
  <div class="mb-4">
    <h2 class="text-lg font-bold text-primary-800">Drift Alerts</h2>
  </div>

  <!-- Table Container -->
  <div class="overflow-x-auto border-2 border-black rounded-lg">
    <div class="h-full flex flex-col min-w-[900px]">
      {#if alerts.length === 0}
        <!-- Empty State -->
        <div class="flex items-center justify-center p-12 bg-white">
          <p class="text-lg font-bold text-gray-500">No alerts to display</p>
        </div>
      {:else}
        <!-- Header -->
        <div class="bg-white border-b-2 border-black sticky top-0 z-10">
          <div class="grid grid-cols-[80px_120px_1fr_100px_140px_180px] gap-2 text-black text-sm font-heading px-2 py-2">
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">ID</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Type</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Name</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Details</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Status</span>
            </div>
            <div class="text-center">
              <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">Created</span>
            </div>
          </div>
        </div>

        <!-- Rows -->
        <div class="bg-white">
          {#each alerts as alert, i}
            <div
              class="grid grid-cols-[80px_120px_1fr_100px_140px_180px] gap-2 items-center px-2 py-2 border-b border-gray-200 transition-colors {i % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-primary-200"
            >
              <!-- ID -->
              <div class="text-center">
                <span class="text-xs font-mono text-gray-500">{alert.id}</span>
              </div>

              <!-- Drift Type Badge -->
              <div class="text-center">
                <span class="px-2 py-1 rounded-lg border-2 text-xs font-medium {getDriftTypeBadge(alert.drift_type)}">
                  {alert.drift_type.toUpperCase()}
                </span>
              </div>

              <!-- Entity Name -->
              <div class="text-center min-w-0">
                <span class="text-xs text-black font-medium truncate">
                  {alert.entity_name}
                </span>
              </div>

              <!-- Details Modal -->
              <div class="flex justify-center">
                <CodeModal name='Alert' code={JSON.stringify(alert.alert, null, 2)} />
              </div>

              <!-- Acknowledge Button -->
              <div class="flex justify-center">
                <button
                  class="btn text-xs px-3 py-1 bg-error-500 hover:bg-error-600 text-white border-2 border-black shadow-small shadow-hover-small rounded-lg font-bold transition-all"
                  onclick={() => updateAlert(alert.id, alert.space)}
                >
                  Acknowledge
                </button>
              </div>

              <!-- Created Date -->
              <div class="text-center">
                <span class="text-xs text-black font-mono">
                  {formatTimestamp(alert.created_at)}
                </span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Pagination Controls -->
  {#if alerts.length > 0}
    <div class="flex justify-center pt-4 gap-2 items-center">
      {#if driftAlerts.has_previous}
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
          onclick={handlePreviousPage}
        >
          <ArrowLeft color="#5948a3"/>
        </button>
      {/if}
      
      {#if driftAlerts.has_next}
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