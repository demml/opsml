<script lang="ts">
  import type { StringStats } from "./types";
  import WordBarChart from "$lib/components/viz/WordBarChart.svelte";

  let { stringData } = $props<{ stringData: StringStats }>();
  let resetZoom: boolean = $state(false);

  function resetZoomClicked() {
    resetZoom = !resetZoom;
  }
</script>

<div class="flex flex-wrap gap-4 pt-2 w-full">
  <!-- Stats section -->
  <div class="flex flex-row flex-wrap gap-4 items-center w-full md:w-1/4">
    <!-- General stats card -->
    <div class="flex flex-col gap-1 border-2 border-black rounded-lg bg-surface-50 min-w-[125px] flex-1">
      <div class="flex items-center justify-center bg-primary-100 border-b-2 border-primary-950 rounded-t-lg">
        <div class="font-bold text-primary-950">Stats</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Distinct:</div>
        <div class="text-black text-sm">{stringData.distinct.count} ({stringData.distinct.percent}%)</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Min Length:</div>
        <div class="text-black text-sm">{stringData.char_stats.min_length}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Max Length:</div>
        <div class="text-black text-sm">{stringData.char_stats.max_length}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Median Length:</div>
        <div class="text-black text-sm">{stringData.char_stats.median_length}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Mean Length:</div>
        <div class="text-black text-sm">{stringData.char_stats.mean_length}</div>
      </div>
    </div>
  </div>

  <!-- Chart section -->
  <div class="flex-1 min-w-[260px] w-full md:w-2/3 flex flex-col">
    <div class="flex flex-row flex-wrap pb-1 items-center justify-between w-full">
      <div class="font-bold text-primary-950">Word Occurrence (Top 10)</div>
      <button
        class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center"
        type="button"
        onclick={resetZoomClicked}
        aria-label="Reset Zoom"
      >
        <div class="text-black">Reset Zoom</div>
      </button>
    </div>
    <div class="w-full h-[220px] sm:h-[300px] lg:h-[340px]">
      <WordBarChart
        wordStats={stringData.word_stats}
        bind:resetZoom={resetZoom}
      />
    </div>
  </div>
</div>