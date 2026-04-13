
<script lang="ts">
    import type { AlertCondition } from "$lib/components/scouter/types";
    import Pill from '$lib/components/utils/Pill.svelte';

    let {
      alertInfo
    } = $props<{
      alertInfo: AlertCondition
    }>();

  </script>

{#if alertInfo}
    <Pill key="Baseline" value={alertInfo.baseline_value} textSize="text-sm"/>
    <Pill key="Threshold" value={alertInfo.alert_threshold} textSize="text-sm"/>
  {#if alertInfo.delta}
    <Pill key="Threshold Value" value={alertInfo.delta} textSize="text-sm"/>
  {/if}

{/if}
