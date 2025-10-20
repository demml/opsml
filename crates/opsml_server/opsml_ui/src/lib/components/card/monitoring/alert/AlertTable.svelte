<script lang="ts">
  import type { Alert } from "./types";
  import CodeModal from "../CodeModal.svelte";

let { 
    alerts, // need to make an effect that updates this when the alerts change
    updateAlert
  } = $props<{
    alerts: Alert[];
    updateAlert: (id: number, space: string) => Promise<void>;
  }>();



</script>

<div class="flex flex-col h-full">
    <div class="items-center mr-2 font-bold text-primary-800">Drift Alerts</div>
  {#if alerts.length === 0}
    <div class="flex items-center justify-center flex-1 text-center text-gray-500 text-lg text-primary-500 font-bold">
      No alerts to display
    </div>
  {:else}
    <div class="overflow-auto w-full">
      <table class="text-black border-collapse text-sm bg-white w-full">
        <thead class="sticky top-0 z-5 bg-white" style="box-shadow: 0 2px 0 0 #000;">
          <tr>
            <th class="p-2 font-heading pl-6 text-left text-black">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                ID
              </span>
            </th>
            <th class="p-2 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Drift Type
              </span>
            </th>
            <th class="p-2 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Name
              </span>
            </th>
            <th class="p-2 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Details
              </span>
            </th>
            <th class="p-2 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Status
              </span>
            </th>
            <th class="p-2 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Created At
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          {#each alerts as alert, i}
          <tr class={`border-b-2 border-black hover:bg-primary-300 py-2 ${i % 2 === 0 ? 'bg-gray-100' : 'bg-white'}`}>
            <td class="p-1 pl-8">{alert.id}</td>
            <td class="p-1 text-center">
              <span class={`px-2 py-1 rounded-full border border-black text-xs ${
                alert.drift_type === 'spc' ? 'bg-yellow-100 text-yellow-800' :
                alert.drift_type === 'psi' ? 'bg-blue-100 text-blue-800' :
                alert.drift_type === 'custom' ? 'bg-green-100 text-green-800' :
                'bg-primary-100 text-primary-800'
              }`}>
                {alert.drift_type}
              </span>
            </td>
            <td class="p-1 text-center">{alert.entity_name}</td>
            <td class="p-1 text-center"><CodeModal name='Alert' code={alert.alert} /></td>
            <td class="pr-4 py-2 text-black">
              <div class="flex justify-center items-center">
                <button class="btn text-sm flex flex-row gap-2 bg-error-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() =>  updateAlert(alert.id, alert.space)}>
                  <div class="text-black">Acknowledge</div>
                </button>
              </div>
            </td>
            <td class="p-1 text-center text-xs">{alert.created_at}</td>
          </tr>
        {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

