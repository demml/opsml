<script lang="ts">
  let { min, max, onApply } = $props<{
    min?: number;
    max?: number;
    onApply: (next: { min?: number; max?: number }) => void;
  }>();

  let localMin = $state<string>(min !== undefined ? String(min) : "");
  let localMax = $state<string>(max !== undefined ? String(max) : "");

  function apply() {
    const nextMin = localMin === "" ? undefined : Number(localMin);
    const nextMax = localMax === "" ? undefined : Number(localMax);
    onApply({
      min: nextMin !== undefined && !Number.isNaN(nextMin) ? nextMin : undefined,
      max: nextMax !== undefined && !Number.isNaN(nextMax) ? nextMax : undefined,
    });
  }

  function clear() {
    localMin = "";
    localMax = "";
    onApply({});
  }
</script>

<div class="space-y-2">
  <div class="flex items-center gap-2">
    <input
      type="number"
      min="0"
      step="1"
      bind:value={localMin}
      placeholder="min ms"
      class="w-full px-2 py-1 text-xs font-mono border-2 border-black bg-white text-primary-800 rounded-base"
    />
    <span class="text-xs text-gray-500">-</span>
    <input
      type="number"
      min="0"
      step="1"
      bind:value={localMax}
      placeholder="max ms"
      class="w-full px-2 py-1 text-xs font-mono border-2 border-black bg-white text-primary-800 rounded-base"
    />
  </div>
  <div class="flex items-center gap-2">
    <button
      type="button"
      onclick={apply}
      class="px-2 py-1 text-xs font-black uppercase tracking-wide border-2 border-black bg-primary-500 text-white rounded-base shadow-small"
    >
      Apply
    </button>
    <button
      type="button"
      onclick={clear}
      class="px-2 py-1 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small"
    >
      Clear
    </button>
  </div>
  <p class="text-[10px] text-gray-500 font-mono">
    Server-backed trace duration filter
  </p>
</div>
