<script lang="ts">
  import type { DriftAlertPaginationResponse, Alert } from "../alert/types";
  import type { RecordCursor } from "../types";
  import { ArrowLeft, ArrowRight, Bell } from 'lucide-svelte';

  let {
    driftAlerts,
    onUpdateAlert,
    onPageChange,
    space
  } = $props<{
    driftAlerts: DriftAlertPaginationResponse;
    onUpdateAlert: (id: number, space: string) => Promise<void>;
    onPageChange: (cursor: RecordCursor, direction: string) => Promise<void>;
    space: string;
  }>();

  let alerts = $derived(driftAlerts);
  let alertItems: Alert[] = $derived(driftAlerts.items || []);


  async function handleNextPage() {
    if (alerts.has_next && alerts.next_cursor && onPageChange) {
      await onPageChange(alerts.next_cursor, 'next');
    }
  }

  async function handlePreviousPage() {
    if (alerts.has_previous && alerts.previous_cursor && onPageChange) {
      await onPageChange(alerts.previous_cursor, 'previous');
    }
  }

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true
    });
  }

  function formatNumber(num: number | string): string {
    return typeof num === 'number' ? num.toLocaleString('en-US', { maximumFractionDigits: 4 }) : num;
  }
</script>

<div class="h-full pt-2 w-full min-w-0">
  <div class="border-2 border-black rounded-lg bg-white h-full max-h-[500px] w-full grid grid-rows-[1fr_auto] overflow-hidden">
    
    <div class="bg-slate-50 w-full overflow-auto relative min-h-0">
      {#if alertItems.length === 0}
        <div class="flex flex-col items-center justify-center p-8 h-full gap-2">
          <Bell class="w-8 h-8 text-gray-300" />
          <p class="text-sm font-bold text-gray-500">No active alerts</p>
        </div>
      {:else}
        <table class="w-full border-collapse text-left whitespace-nowrap">
            <thead class="bg-white text-xs uppercase text-slate-500 sticky top-0 z-10 shadow-sm">
                <tr>
                    <th class="py-3 px-4 font-black text-center border-b-2 border-black bg-white">ID</th>
                    <th class="py-3 px-4 font-black text-center border-b-2 border-black bg-white">Created</th>
                    <th class="py-3 px-4 font-black text-left border-b-2 border-black bg-white">Feature</th>
                    <th class="py-3 px-4 font-black text-center border-b-2 border-black bg-white">Drift Kind</th>
                    <th class="py-3 px-4 font-black text-center border-b-2 border-black bg-white">Drift Zone</th>
                    <th class="py-3 px-4 font-black text-center border-b-2 border-black bg-white">Status</th>
                    <th class="py-3 px-4 font-black text-center border-b-2 border-black bg-white">Action</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
                {#each alertItems as alert}
                  {@const alertData = alert.alert.Spc}
                  <tr class="hover:bg-primary-50 transition-colors">
                    <td class="py-3 px-4 text-center">
                        <span class="font-mono font-bold text-xs text-slate-500">#{alert.id}</span>
                    </td>
                    <td class="py-3 px-4 text-center text-xs font-mono text-slate-700">
                        {formatTimestamp(alert.created_at)}
                    </td>
                    <td class="py-3 px-4 text-xs font-bold text-slate-900">
                        <div class="truncate" title={alertData.feature}>
                          {alertData.feature}
                        </div>
                    </td>
                    <td class="py-3 px-4 text-center text-xs font-mono text-black font-bold">
                        {alertData.kind}
                    </td>
                    <td class="py-3 px-4 text-center text-xs font-mono text-error-700 font-bold">
                        {alertData.zone}
                    </td>
                    <td class="py-3 px-4 text-center">
                        <span class="px-2 py-1 rounded border text-[10px] font-black uppercase {alert.active ? 'bg-error-100 border-error-900 text-error-900' : 'bg-gray-100 border-gray-500 text-gray-500'}">
                            {alert.active ? 'Active' : 'Done'}
                        </span>
                    </td>
                    <td class="py-3 px-4 text-center">
                        <button
                            class="text-[10px] px-3 py-1.5 bg-error-500 hover:bg-error-600 text-white border-2 border-black rounded font-bold transition-all shadow-small active:translate-y-[1px] active:shadow-none"
                            onclick={() => onUpdateAlert(alert.id, space)}
                          >
                            Ack
                          </button>
                    </td>
                  </tr>
                {/each}
            </tbody>
        </table>
      {/if}
    </div>

    {#if alertItems.length > 0}
      <div class="border-t-2 border-black bg-gray-50 p-2 flex justify-center gap-2 items-center z-20">
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9 px-3 flex items-center justify-center disabled:opacity-50 disabled:shadow-none disabled:translate-y-[2px]"
          onclick={handlePreviousPage}
          disabled={!alerts.has_previous}
        >
          <ArrowLeft class="w-4 h-4" color="#5948a3"/>
        </button>

        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9 px-3 flex items-center justify-center disabled:opacity-50 disabled:shadow-none disabled:translate-y-[2px]"
          onclick={handleNextPage}
          disabled={!alerts.has_next}
        >
          <ArrowRight class="w-4 h-4" color="#5948a3"/>
        </button>
      </div>
    {/if}
  </div>
</div>