<script lang="ts">
  import type { NumericStats } from "./types";
  import HistChart from "$lib/components/viz/HistChart.svelte";

  let { numericData } = $props<{ numericData: NumericStats }>();

  let resetZoomTrigger: number = $state(0);
  let resetZoomClicked = () => {
    resetZoomTrigger++;
  }
</script>


<div class="flex flex-wrap gap-4 pt-2 w-full">
  <!-- Stats section -->
  <div class="flex flex-row flex-wrap gap-4 items-center w-full md:w-1/4">
    <!-- General stats -->
    <div class="flex flex-col gap-1 border-2 border-black rounded-lg bg-surface-50 min-w-[125px] flex-1">
      <div class="flex items-center justify-center bg-primary-100 border-b-2 border-primary-950 rounded-t-lg">
        <div class="font-bold text-primary-950">General Stats</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Distinct:</div>
        <div class="text-black text-sm">{numericData.distinct.count} ({numericData.distinct.percent}%)</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Mean:</div>
        <div class="text-black text-sm">{numericData.stddev.toFixed(3)}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Minimum:</div>
        <div class="text-black text-sm">{numericData.min.toFixed(3)}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Maximum:</div>
        <div class="text-black text-sm">{numericData.max.toFixed(3)}</div>
      </div>
    </div>

    <!-- Quantiles -->
    <div class="flex flex-col gap-1 border-2 border-black rounded-lg bg-surface-50 min-w-[125px] flex-1">
      <div class="flex items-center justify-center bg-primary-100 border-b-2 border-primary-950 rounded-t-lg">
        <div class="font-bold text-primary-950">Quantiles</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Q25:</div>
        <div class="text-black text-sm">{numericData.quantiles.q25.toFixed(3)}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Q50:</div>
        <div class="text-black text-sm">{numericData.quantiles.q50.toFixed(3)}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Q75:</div>
        <div class="text-black text-sm">{numericData.quantiles.q75.toFixed(3)}</div>
      </div>
      <div class="flex flex-row items-center px-2">
        <div class="font-bold text-sm text-primary-800 pr-1">Q99:</div>
        <div class="text-black text-sm">{numericData.quantiles.q99.toFixed(3)}</div>
      </div>
    </div>
  </div>

  <!-- Chart section -->
  <div class="flex-1 min-w-[260px] w-full md:w-2/3 flex flex-col">
    <div class="flex flex-row flex-wrap pb-1 items-center justify-between w-full">
      <div class="font-bold text-primary-950">Distribution</div>
      <button
        class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center"
        type="button"
        onclick={resetZoomClicked}
        aria-label="Reset Zoom"
      >
        <div class="text-black">Reset Zoom</div>
      </button>
    </div>
    <div class="w-full h-[220px] sm:h-[300px] md:h-[340px]">
      <HistChart
        histData={numericData.histogram}
        bind:resetZoomTrigger={resetZoomTrigger}
      />
    </div>
  </div>
</div>