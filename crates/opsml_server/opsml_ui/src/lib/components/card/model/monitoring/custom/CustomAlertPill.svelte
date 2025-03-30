
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
    <Pill key="Baseline" value={value} />  
    <Pill key="Threshold" value={alertInfo.threshold} />  
  {#if alertInfo.number}
    <Pill key="Number" value={alertInfo.number} />  
  {/if}

{/if}
  