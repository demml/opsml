<script lang="ts">

  import { type MonitorAlerts, AlertStatus, type UpdateAlert  } from "$lib/scripts/types";
  import { createEventDispatcher } from 'svelte';
  import { updateMonitorAlert } from "$lib/scripts/monitoring/utils";



  export let alerts: MonitorAlerts;
  const dispatch = createEventDispatcher();

  function formatDate(dateString) {
    const date = new Date(dateString);
    const formattedDate = date.toISOString().split('.')[0];
    return formattedDate;
  }

  async function acknowledgeAlert(alertId: number) {
    // Implement the logic to acknowledge the alert
    
    // update alerts
    let response = await updateMonitorAlert(alertId, AlertStatus.ACKNOWLEDGED) as UpdateAlert;

    if (response.status === "success") {
      // update alerts
      alerts.alerts = alerts.alerts.filter(alert => alert.id !== alertId);
    } else {
      console.log('Failed to acknowledge alert');
    }

  };

  let hoveredAlertId: number | null = null;

  function handleMouseEnter(alertId: number) {
    hoveredAlertId = alertId;
  }

  function handleMouseLeave() {
    hoveredAlertId = null;
  }

  function switchFeature(feature: string) {
    dispatch('switchFeature', {feature});
  }




</script>


<style>
  .center-content {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%; /* Ensure the parent div takes up the full height */
  }
</style>


      {#if alerts.alerts.length === 0}
        <div class="center-content text-center text-gray-500 self-center text-2xl text-secondary-600 font-bold">No alerts to display</div>
      {:else}
      <table class="table-compact table-cell-fit table-hover text-xs text-center min-w-full">
        <thead class="bg-primary-200 sticky top-0">
          <tr>
            <th class="text-sm text-center py-2">Created At</th>
            <th class="text-sm text-center py-2">ID</th>
            <th class="text-sm text-center py-2">Feature</th>
            <th class="text-sm text-center py-2">Kind</th>
            <th class="text-sm text-center py-2">Zone</th>
            <th class="text-sm text-center py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {#each alerts.alerts as alert}
            <tr class="even:bg-gray-100">
              <td class="text-xs">{formatDate(alert.created_at)}</td>
              <td class="text-xs">{alert.id}</td>
              <td class="text-xs"><button type="button" class="badge variant-soft-primary" on:click={() => switchFeature(alert.feature)}>{alert.feature}</button></td>
              <td class="text-xs">{alert.alert["kind"]}</td>
              <td class="text-xs">{alert.alert["zone"]}</td>
              <td class="text-xs">
                <button
                  type="button"
                  class="badge text-xs text-white bg-scouter_red hover:bg-secondary-700"
                  on:click={() => acknowledgeAlert(alert.id)}
                  on:mouseenter={() => handleMouseEnter(alert.id)}
                  on:mouseleave={handleMouseLeave}
                >
                {hoveredAlertId === alert.id ? 'Ack' : 'Active'}
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      {/if}
