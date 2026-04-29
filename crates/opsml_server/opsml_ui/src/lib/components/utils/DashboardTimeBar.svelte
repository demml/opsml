<script lang="ts">
  import TimeRangeFilter from "$lib/components/trace/TimeRangeFilter.svelte";
  import type { TimeRange } from "$lib/components/trace/types";

  let {
    selectedRange,
    refreshing,
    onRangeChange,
    onRefresh,
  }: {
    selectedRange: TimeRange;
    refreshing: boolean;
    onRangeChange: (range: TimeRange) => void;
    onRefresh: () => void;
  } = $props();
</script>

<div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full xl:w-auto">
  <div class="hidden sm:block w-[2px] h-8 bg-black/10 mx-2"></div>
  <div class="w-full sm:w-auto">
    <TimeRangeFilter
      selectedRange={selectedRange}
      onRangeChange={onRangeChange}
    />
  </div>
  <button
    onclick={onRefresh}
    disabled={refreshing}
    class="flex items-center gap-2 px-3 py-2 bg-white border-2 border-black rounded-lg shadow-small hover:bg-primary-50 hover:shadow-hover transition-all duration-100 text-sm font-bold text-black disabled:opacity-50 disabled:cursor-not-allowed"
    title="Refresh data"
    aria-label="Refresh data"
  >
    <svg
      class="w-4 h-4 {refreshing ? 'animate-spin' : ''}"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
      />
    </svg>
  </button>
</div>
