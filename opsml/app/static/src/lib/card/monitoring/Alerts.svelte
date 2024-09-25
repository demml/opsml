<script lang="ts">

  import { type MonitorAlerts  } from "$lib/scripts/types";


  export let alerts: MonitorAlerts;

  function acknowledgeAlert(alertId: string) {
    // Implement the logic to acknowledge the alert
    alerts.alerts = alerts.alerts.filter(alert => alert.id !== alertId);
    console.log(`Acknowledged alert with ID: ${alertId}`);
  };

  let hoveredAlertId: string | null = null;

  function handleMouseEnter(alertId: string) {
    hoveredAlertId = alertId;
  }

  function handleMouseLeave() {
    hoveredAlertId = null;
  }


</script>

    <table class="table-compact table-hover text-xs text-center min-w-full">
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
            <td class="text-sm">{alert.created_at}</td>
            <td class="text-sm">{alert.id}</td>
            <td class="text-sm"><span class="badge variant-soft-primary">{alert.feature}</span></td>
            <td class="text-sm">{alert.alerts["kind"]}</td>
            <td class="text-sm">{alert.alerts["zone"]}</td>
            <td class="text-sm">
              <button
                type="button"
                class="btn bg-blue-500 text-white bg-scouter_red hover:bg-secondary-700"
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
