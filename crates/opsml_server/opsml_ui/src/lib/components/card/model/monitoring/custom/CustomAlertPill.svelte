
<script lang="ts">
    import { type AlertConditionInfo } from './custom';
    import Pill from '$lib/components/utils/Pill.svelte';
  
    let { 
      value,
      alertInfo
    } = $props<{
      value: number,
      alertInfo: AlertConditionInfo
    }>();
  
  </script>

{#if alertInfo}
    <Pill key="Baseline" value={value} textSize="text-sm"/>  
    <Pill key="Threshold" value={alertInfo.threshold} textSize="text-sm"/>  
  {#if alertInfo.number}
    <Pill key="Number" value={alertInfo.number} textSize="text-sm"/>  
  {/if}

{/if}
  