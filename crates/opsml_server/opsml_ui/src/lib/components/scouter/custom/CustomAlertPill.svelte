
<script lang="ts">
    import { type AlertCondition } from '../types';
    import Pill from '$lib/components/utils/Pill.svelte';

    let {
      value,
      alertInfo
    } = $props<{
      value: number,
      alertInfo: AlertCondition
    }>();

  </script>

{#if alertInfo}
    <Pill key="Baseline" value={value} textSize="text-sm"/>
    <Pill key="Threshold" value={alertInfo.alert_threshold} textSize="text-sm"/>
  {#if alertInfo.baseline_value}
    <Pill key="Baseline Value" value={alertInfo.baseline_value} textSize="text-sm"/>
  {/if}

{/if}
