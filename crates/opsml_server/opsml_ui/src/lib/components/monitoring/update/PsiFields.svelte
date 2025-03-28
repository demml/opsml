
<script lang="ts">
    import type { PsiConfigParams, PsiConfigSchema } from "./schema";
  
      let { 
        params = $bindable(),
        errors = $bindable(),
      } = $props<{
        params: PsiConfigParams;
        errors: Partial<Record<keyof PsiConfigSchema, string>>;
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
      Psi Threshold
      <input
        class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
        type="text" 
        placeholder={params.psi_threshold}
        bind:value={params.psi_threshold}
      />
      {#if errors.psi_threshold}
        <span class="text-red-500 text-sm">{errors.psi_threshold}</span>
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
  