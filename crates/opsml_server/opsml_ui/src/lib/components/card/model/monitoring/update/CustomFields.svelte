
<script lang="ts">
  import type { CustomConfigParams, CustomConfigSchema } from "./schema";

    let { 
      params = $bindable(),
      errors = $bindable(),
      updateCallback = $bindable(),
    } = $props<{
      params: CustomConfigParams,
      errors: Partial<Record<keyof CustomConfigSchema, string>>;
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
    Sample
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      value={params.sample}
      oninput={(e) => updateCallback('sample', e.currentTarget.value)}
    />
    {#if errors.sample}
      <span class="text-red-500 text-sm">{errors.sample}</span>
    {/if}
  </label>

  <label class="text-surface-950 text-sm">
    Sample Size
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      value={params.sample_size}
      oninput={(e) => updateCallback('sample_size', e.currentTarget.value)}
    />
    {#if errors.sample_size}
      <span class="text-red-500 text-sm">{errors.sample_size}</span>
    {/if}
  </label>
</div>
