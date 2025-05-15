<script lang="ts">
  import type { Alert } from "./types";
  import AlertModal from "./AlertModal.svelte";


let { 
    alerts,
    acknowledgeAlert,
  } = $props<{
    alerts: Alert[];
    acknowledgeAlert: (id: string) => void;
  }>();



</script>


{#if alerts.length === 0}
<div class="h-full border-2 border-black flex items-center justify-center">
  <div class="text-center text-gray-500 text-2xl text-primary-500 font-bold">
    No alerts to display
  </div>
</div>
{:else}
<div class="h-full overflow-auto rounded-lg border-2 border-black">
  <table class="w-full text-black text-sm md:text-base bg-slate-100">
    <thead class="bg-primary-500 sticky top-0">
      <tr>
        <th class="text-black pl-4 py-2 text-left">Created At</th>
        <th class="text-black p-2">Id</th>
        <th class="text-black p-2">Drift Type</th>
        <th class="text-black p-2">Name</th>
        <th class="text-black p-2">Details</th>
        <th class="text-black pr-4 py-2">Status</th>
      </tr>
    </thead>
    <tbody>
      {#each alerts as alert}
      <tr class="border-t hover:bg-primary-300 py-2">
        <td class="pl-4 py-2">{alert.created_at}</td>
        <td class="p-2 text-center">{alert.id}</td>
        <td class="p-2 text-center">{alert.drift_type}</td>
        <td class="p-2 text-center">{alert.feature}</td>
        <td class="p-2 text-center" ><AlertModal code={JSON.stringify(alert.alert)} /></td>
        <td class="pr-4 py-2 text-black">
          <div class="flex justify-center items-center">
            <button class="btn flex flex-row gap-2 bg-error-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => acknowledgeAlert(alert.id)}>
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
