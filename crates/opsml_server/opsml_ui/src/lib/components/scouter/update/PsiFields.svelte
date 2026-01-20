
<script lang="ts">
  import { onMount } from "svelte";
  import {  type PsiConfigParams, type PsiConfigSchema } from "./schema";
  import {  type PsiThreshold } from "../psi/types";
  import { getPsiThresholdKeyValue, updatePsiThreshold,  } from "../psi/utils";

    let { 
      params = $bindable(),
      errors = $bindable(),
      updateCallback = $bindable(),
    } = $props<{
      params: PsiConfigParams;
      errors: Partial<Record<keyof PsiConfigSchema, string>>;
      updateCallback: (field: string, value: string | PsiThreshold) => void;
    }>();

    // $state
    let thresholdType = $state<string>("Fixed");
    let thresholdValue = $state<number>(0.1);


    onMount(() => {
      // Initialize from params only once
      const initial = getPsiThresholdKeyValue(params.threshold);
      thresholdType = initial.type;
      thresholdValue = initial.value;
    });

    
    function handleThresholdBlur() {
      const threshold = updatePsiThreshold(thresholdType, thresholdValue);
      updateCallback('threshold', threshold);
    }


  
  </script>
  
  <div class="grid grid-cols-1 gap-3 ">
    <label class="text-surface-950 text-sm">
      Schedule
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        value={params.schedule}
        oninput={(e) => updateCallback('schedule', e.currentTarget.value)}
      />
      {#if errors.schedule}
        <span class="text-red-500 text-sm">{errors.schedule}</span>
      {/if}
    </label>

     <label class="text-surface-950 text-sm">
      Psi Threshold Type
      <select
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        bind:value={thresholdType}
        onchange={handleThresholdBlur}
      >
        <option value="Normal">Normal</option>
        <option value="ChiSquare">ChiSquare</option>
        <option value="Fixed">Fixed</option>
      </select>
      {#if errors.psi_threshold_type}
        <span class="text-red-500 text-sm">{errors.psi_threshold_type}</span>
      {/if}
    </label>
  
    <label class="text-surface-950 text-sm">
      Psi Threshold Value
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        bind:value={thresholdValue}
        onblur={handleThresholdBlur}
      />
      {#if errors.psi_threshold_value}
        <span class="text-red-500 text-sm">{errors.psi_threshold_value}</span>
      {/if}
    </label>

    <label class="text-surface-950 text-sm">
      Features to monitor
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        value={params.features_to_monitor}
        oninput={(e) => updateCallback('features_to_monitor', e.currentTarget.value)}
      />
      {#if errors.features_to_monitor}
        <span class="text-red-500 text-sm">{errors.features_to_monitor}</span>
      {/if}
    </label>
  </div>
  