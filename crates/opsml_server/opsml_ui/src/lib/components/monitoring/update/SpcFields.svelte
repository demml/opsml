
<script lang="ts">
  import type { SpcConfigParams, SpcConfigSchema } from "./schema";

    let { 
      params = $bindable(),
      errors = $bindable(),
    } = $props<{
      params: SpcConfigParams;
      errors: Partial<Record<keyof SpcConfigSchema, string>>;
    }>();
</script>

<div class="grid grid-cols-1 gap-3 ">
  <label class="text-surface-950">
    Schedule
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      placeholder={params.schedule}
      bind:value={params.schedule}
    />
    {#if errors.schedule}
      <span class="text-red-500 text-sm">{errors.schedule}</span>
    {/if}
  </label>

  <label class="text-surface-950">
    Sample
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      placeholder={params.sample}
      bind:value={params.sample}
    />
    {#if errors.sample}
      <span class="text-red-500 text-sm">{errors.sample}</span>
    {/if}
  </label>

  <label class="text-surface-950">
    Sample Size
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      placeholder={params.sample_size}
      bind:value={params.sample_size}
    />
    {#if errors.sample_size}
      <span class="text-red-500 text-sm">{errors.sample_size}</span>
    {/if}
  </label>

  <label class="text-surface-950">
    Rule
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      placeholder={params.rule}
      bind:value={params.rule}
    />
    {#if errors.rule}
      <span class="text-red-500 text-sm">{errors.rule}</span>
    {/if}
  </label>

  <label class="text-surface-950">
    Features to monitor
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text" 
      placeholder={params.features_to_monitor}
      bind:value={params.features_to_monitor}
    />
    {#if errors.features_to_monitor}
      <span class="text-red-500 text-sm">{errors.features_to_monitor}</span>
    {/if}
  </label>
</div>
