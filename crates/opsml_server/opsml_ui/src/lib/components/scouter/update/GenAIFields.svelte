
<script lang="ts">
  import type { GenAIConfigParams, GenAIConfigSchema } from "./schema";

    let {
      params = $bindable(),
      errors = $bindable(),
      updateCallback = $bindable(),
    } = $props<{
      params: GenAIConfigParams,
      errors: Partial<Record<keyof GenAIConfigSchema, string>>;
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
    Sample Ratio
    <input
      class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
      type="text"
      value={params.sample_ratio}
      oninput={(e) => updateCallback('sample_ratio', e.currentTarget.value)}
    />
    {#if errors.sample_ratio}
      <span class="text-red-500 text-sm">{errors.sample_ratio}</span>
    {/if}
  </label>
</div>
