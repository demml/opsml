
<script lang="ts">
  import type { CustomConfigParams, CustomConfigSchema } from "./schema";

    let { 
      params = $bindable(),
      errors = $bindable(),
    } = $props<{
      params: CustomConfigParams,
      errors: Partial<Record<keyof CustomConfigSchema, string>>;
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
        bind:value={params.samplee}
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
   
  </div>
