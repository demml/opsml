
<script lang="ts">
    import { type LLMMetricAlertCondition } from './llm';
    import Pill from '$lib/components/utils/Pill.svelte';
  
    let { 
      value,
      alertInfo
    } = $props<{
      value: number,
      alertInfo: LLMMetricAlertCondition
    }>();
  
  </script>

{#if alertInfo}
    <Pill key="Baseline" value={value} textSize="text-sm"/>  
    <Pill key="Threshold" value={alertInfo.alert_threshold} textSize="text-sm"/>  
  {#if alertInfo.alert_threshold_value}
    <Pill key="Threshold Value" value={alertInfo.alert_threshold_value} textSize="text-sm"/>  
  {/if}

{/if}
  