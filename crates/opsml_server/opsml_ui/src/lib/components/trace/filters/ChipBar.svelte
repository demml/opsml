<script lang="ts">
  import { Plus, X } from "lucide-svelte";
  import type { ActiveFilter, FacetCount } from "../types";
  import AddFilterMenu from "./AddFilterMenu.svelte";

  let {
    chips,
    services,
    statuses,
    onRemove,
    onAddService,
    onAddStatus,
    onAddHasErrors,
    onAddAttribute,
    onAddDuration,
  } = $props<{
    chips: ActiveFilter[];
    services: FacetCount[];
    statuses: FacetCount[];
    onRemove: (chip: ActiveFilter) => void;
    onAddService: (service: string) => void;
    onAddStatus: (status: number) => void;
    onAddHasErrors: () => void;
    onAddAttribute: (raw: string) => void;
    onAddDuration: (min?: number, max?: number) => void;
  }>();

  let menuOpen = $state(false);
</script>

<div class="flex flex-wrap items-center gap-2 px-4 py-2 border-2 border-black bg-surface-50 rounded-base shadow">
  {#if chips.length === 0}
    <span class="text-xs font-mono text-gray-400">No filters · click + Add filter</span>
  {/if}

  {#each chips as chip (`${chip.key}:${chip.value}`)}
    <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-white text-primary-800 rounded-base shadow-small">
      <span class="text-primary-600 font-mono uppercase tracking-wide text-[10px]">{chip.label}:</span>
      <span class="font-mono">{chip.value}</span>
      <button
        type="button"
        onclick={() => onRemove(chip)}
        class="ml-1 p-0.5 rounded-base hover:bg-error-100 transition-colors duration-100"
        aria-label={`Remove ${chip.label}:${chip.value}`}
      >
        <X class="w-3 h-3" />
      </button>
    </span>
  {/each}

  <div class="relative">
    <button
      type="button"
      onclick={() => (menuOpen = !menuOpen)}
      class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-dashed border-black bg-surface-100 hover:bg-warning-200 rounded-base shadow-small transition-colors duration-100"
    >
      <Plus class="w-3 h-3" />
      Add filter
    </button>

    {#if menuOpen}
      <AddFilterMenu
        {services}
        {statuses}
        onClose={() => (menuOpen = false)}
        {onAddService}
        {onAddStatus}
        {onAddHasErrors}
        {onAddAttribute}
        {onAddDuration}
      />
    {/if}
  </div>
</div>
