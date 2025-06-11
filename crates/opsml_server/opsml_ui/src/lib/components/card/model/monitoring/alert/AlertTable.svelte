<script lang="ts">
  import type { Alert } from "./types";
  import AlertModal from "./AlertModal.svelte";



let { 
    alerts, // need to make an effect that updates this when the alerts change
    updateAlert
  } = $props<{
    alerts: Alert[];
    updateAlert: (id: number, space: string) => Promise<void>;
  }>();



</script>

<div class="flex flex-col h-full">
  {#if alerts.length === 0}
    <div class="flex items-center justify-center flex-1 text-center text-gray-500 text-lg text-primary-500 font-bold">
      No alerts to display
    </div>
  {:else}
    <div class="overflow-auto rounded-lg pb-2 border-1 border-black">
      <table class="w-full text-black text-sm bg-slate-100">
        <thead class="bg-primary-500 sticky top-0">
          <tr>
            <th class="text-black text-sm pl-4 py-2 text-left">Created At</th>
            <th class="text-black text-sm p-2">Id</th>
            <th class="text-black text-sm p-2">Drift Type</th>
            <th class="text-black text-sm p-2">Name</th>
            <th class="text-black text-sm p-2">Details</th>
            <th class="text-black text-sm pr-4 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {#each alerts as alert}
          
          <tr class="border-t hover:bg-primary-300 py-2">
            <td class="pl-4 text-sm py-2">{alert.created_at}</td>
            <td class="p-2 text-sm text-center">{alert.id}</td>
            <td class="p-2 text-sm text-center">{alert.drift_type}</td>
            <td class="p-2 text-sm text-center">{alert.entity_name}</td>
            <td class="p-2 text-sm text-center" ><AlertModal code={alert.alert} /></td>
            <td class="pr-4 py-2 text-black">
              <div class="flex justify-center items-center">
                <button class="btn text-sm flex flex-row gap-2 bg-error-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() =>  updateAlert(alert.id, alert.space)}>
                  <div class="text-black">Acknowledge</div>
                </button>
              </div>
            </td>
          </tr>
        {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

