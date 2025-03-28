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
<div class="center-content text-center text-gray-500 self-center text-2xl text-primary-500 font-bold">No alerts to display</div>
{:else}
  <table class="table-auto w-full text-black rounded-lg overflow-hidden text-sm md:text-base bg-slate-100">
    <thead class="bg-primary-500">
      <tr>
        <th class="text-black pl-4 py-2 text-left">Created At</th>
        <th class="text-black p-2 text-left">Id</th>
        <th class="text-black p-2 text-left">Feature</th>
        <th class="text-black p-2 text-left">Details</th>
        <th class="text-black pr-4 py-2 text-right">Status</th>
      </tr>
    </thead>
  </table>
  <tbody>
    {#each alerts as alert}
      <tr class="border-t hover:bg-primary-300 py-2">
        <td class="pl-4 py-2">
          {alert.created_at}
        </td>
        <td class="p-2">
          {alert.id}
        </td>
        <td class="p-2">
          {alert.feature}
        </td>
        <td class="p-2">
          <AlertModal code={JSON.stringify(alert.alert)} />
        </td>
        <td class="pr-4 py-2 text-black text-right">
          <button class="btn flex flex-row gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => acknowledgeAlert(alert.id)}>
            <div class="text-black">Acknowledge</div>
          </button>
        </td>
      </tr>
    {/each}
  </tbody>
{/if}


