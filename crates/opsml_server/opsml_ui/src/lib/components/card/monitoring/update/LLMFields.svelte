
<script lang="ts">
  import type { LlmConfigParams, LlmConfigSchema } from "./schema";

    let { 
      params = $bindable(),
      errors = $bindable(),
      updateCallback = $bindable(),
    } = $props<{
      params: LlmConfigParams,
      errors: Partial<Record<keyof LlmConfigSchema, string>>;
      updateCallback: (field: string, value: string) => void;
    }>();

   
    
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
    Sample Rate
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      value={params.sample_rate}
      oninput={(e) => updateCallback('sample_rate', e.currentTarget.value)}
    />
    {#if errors.sample_rate}
      <span class="text-red-500 text-sm">{errors.sample_rate}</span>
    {/if}
  </label>
</div>
