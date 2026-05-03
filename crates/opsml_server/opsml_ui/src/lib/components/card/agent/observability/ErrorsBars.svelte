<script lang="ts">
  import { AlertTriangle } from 'lucide-svelte';
  import type { GenAiErrorCount } from './types';

  let { errors }: { errors: GenAiErrorCount[] } = $props();
</script>

<div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
  <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
    <AlertTriangle class="w-3 h-3 text-error-700" />
    <span class="text-xs font-black uppercase tracking-wide text-primary-800">Errors</span>
  </div>
  <div class="p-2 space-y-1.5">
    {#if errors.length === 0}
      <p class="text-xs text-primary-700 py-2 text-center">No errors</p>
    {:else}
      {@const max = Math.max(1, ...errors.map((x) => x.count))}
      {#each errors as e (e.error_type)}
        {@const pct = (e.count / max) * 100}
        <div class="flex items-center gap-2">
          <div class="text-xs font-mono font-bold text-primary-900 truncate w-32">{e.error_type}</div>
          <div class="flex-1 h-3 bg-surface-100 border-2 border-black rounded-base overflow-hidden">
            <div class="h-full bg-error-300" style="width: {pct}%"></div>
          </div>
          <div class="text-xs font-mono text-primary-900 w-10 text-right">{e.count}</div>
        </div>
      {/each}
    {/if}
  </div>
</div>
