<script lang="ts">
  import { type AlertDispatchConfig,  type SlackDispatchConfig } from '$lib/components/card/monitoring/types';
  import Dropdown from '$lib/components/utils/Dropdown.svelte';

    let { 

      dispatchConfig= $bindable(),
      errors = $bindable(),
      updateCallback = $bindable(),
   
    } = $props<{
      dispatchConfig: AlertDispatchConfig,
      errors: Partial<Record<keyof SlackDispatchConfig, string>>,
      updateCallback: (field: string, value: string) => void;
    }>();
    
      
    let slackChannel = $state(dispatchConfig?.Slack?.channel ?? '');


  </script>
    

  <div class="grid grid-cols-1 gap-3">

    <label class="text-surface-950 text-sm">
      Slack Channel
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        value={slackChannel}
        oninput={(e) => updateCallback('channel', e.currentTarget.value)}
      />
      {#if errors.channel}
        <span class="text-red-500 text-sm">{errors.channel}</span>
      {/if}
    </label>

  </div>




  

    
    
    