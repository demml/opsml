
<script lang="ts">
  import type { SpcConfigParams, SpcConfigSchema } from "./schema";

    let { 
      params = $bindable(),
      errors = $bindable(),
      updateCallback = $bindable(),
    } = $props<{
      params: SpcConfigParams;
      errors: Partial<Record<keyof SpcConfigSchema, string>>;
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

  <label class="text-surface-950 text-sm">
    Rule
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      placeholder={params.rule}
      oninput={(e) => updateCallback('rule', e.currentTarget.value)}
    />
    {#if errors.rule}
      <span class="text-red-500 text-sm">{errors.rule}</span>
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
