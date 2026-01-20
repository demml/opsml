<script lang="ts">
    import {  type AlertDispatchConfig, } from '$lib/components/scouter/types';
    import { type ConsoleConfigSchema,  } from '../schema';
  
    let { 
  
      dispatchConfig= $bindable(),
      errors = $bindable(),
      updateCallback = $bindable(),
    
    } = $props<{
      dispatchConfig: AlertDispatchConfig,
      errors: Partial<Record<keyof ConsoleConfigSchema, string>>,
      updateCallback: (field: string, value: string) => void;
    }>();


    let consoleEnabled = $state(dispatchConfig?.Console?.enabled ?? '');
    

  
  </script>
    
  <div class="grid grid-cols-1 gap-3">

    <label class="text-surface-950 text-sm">
      Enabled
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        value={consoleEnabled}
        oninput={(e) => updateCallback('enabled', e.currentTarget.value)}
      />
      {#if errors.enabled}
        <span class="text-red-500 text-sm">{errors.enabled}</span>
      {/if}
    </label>

  </div>
  
      