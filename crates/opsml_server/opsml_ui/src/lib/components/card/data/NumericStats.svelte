<script lang="ts">
  import type { NumericStats } from "./types";
  import HistChart from "$lib/components/viz/HistChart.svelte";


let { 
  numericData
} = $props<{
  numericData: NumericStats;
}>();

  let resetZoom: boolean = $state(false);
  
  let resetZoomClicked = () => {
    resetZoom = !resetZoom;
  }

</script>

<div class="grid grid-cols-1 xl:grid-cols-6 gap-2 min-w-max h-auto pt-2">
  <div class="col-span-1 md:col-span-2 h-[350px] flex items-center">
    <div class="flex flex-row flex-wrap justify-center gap-2 items-center p-2 w-full">

      <!-- General stats -->
      <div class="flex flex-col gap-1 border-2 border-black rounded-lg bg-surface-50">
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
      <div class="flex flex-col gap-1 border-2 border-black rounded-lg bg-surface-50">
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

  </div>
  <div class="col-span-1 xl:col-span-4 w-full h-[350px]">

    <div class="flex flex-row flex-wrap pb-1 items-center justify-between w-full">
      <div class="flex items-center justify-center">
        <div class="font-bold text-primary-950">Distribution</div>
      </div>
      <button class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
        <div class="text-black">Reset Zoom</div>
      </button>
    </div>

    <div class="h-[320px]">
      <HistChart 
        histData={numericData.histogram}
        bind:resetZoom={resetZoom}
      />
    </div>

  </div>
</div>