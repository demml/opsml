<script lang="ts">
  import { type AlertDispatchConfig } from '$lib/components/card/monitoring/types';
  import { type OpsGenieConfigSchema,  } from '../schema';
  

  let { 

    dispatchConfig= $bindable(),
    errors = $bindable(),
    updateCallback = $bindable(),
  
  } = $props<{
    dispatchConfig: AlertDispatchConfig,
    errors: Partial<Record<keyof OpsGenieConfigSchema, string>>,
    updateCallback: (field: string, value: string) => void;
  }>();

  let opsGenieTeam = $state(dispatchConfig?.OpsGenie?.team ?? '');
  let opsGeniePriority = $state(dispatchConfig?.OpsGenie?.priority ?? '');
  
  

</script>
    
  <div class="grid grid-cols-1 gap-3">

    <label class="text-surface-950 text-sm">
      OpsGenie Team
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        value={opsGenieTeam}
        oninput={(e) => updateCallback('team', e.currentTarget.value)}
      />
      {#if errors.team}
        <span class="text-red-500 text-sm">{errors.team}</span>
      {/if}
    </label>

    <label class="text-surface-950 text-sm">
      OpsGenie Priority
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        value={opsGeniePriority}
        oninput={(e) => updateCallback('priority', e.currentTarget.value)}
      />
      {#if errors.priority}
        <span class="text-red-500 text-sm">{errors.priority}</span>
      {/if}
    </label>
    
</div>

    