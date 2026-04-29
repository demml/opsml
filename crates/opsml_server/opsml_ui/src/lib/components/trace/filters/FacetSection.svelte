<script lang="ts">
  import { ChevronDown, ChevronUp } from "lucide-svelte";
  import type { Snippet } from "svelte";

  let {
    label,
    count,
    children,
    defaultOpen = true,
  } = $props<{
    label: string;
    count?: number;
    children: Snippet;
    defaultOpen?: boolean;
  }>();

  let open = $state(defaultOpen);
</script>

<div class="border-b-2 border-black last:border-b-0">
  <button
    type="button"
    onclick={() => (open = !open)}
    class="w-full flex items-center justify-between px-3 py-2 bg-white hover:bg-primary-100 transition-colors duration-100"
  >
    <span class="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-primary-800">
      {label}
      {#if count !== undefined}
        <span class="px-1.5 py-0.5 text-[10px] font-mono bg-surface-200 border border-black rounded-base">
          {count}
        </span>
      {/if}
    </span>
    {#if open}
      <ChevronUp class="w-3.5 h-3.5 text-primary-700" />
    {:else}
      <ChevronDown class="w-3.5 h-3.5 text-primary-700" />
    {/if}
  </button>
  {#if open}
    <div class="px-3 py-2 bg-surface-50">
      {@render children()}
    </div>
  {/if}
</div>
