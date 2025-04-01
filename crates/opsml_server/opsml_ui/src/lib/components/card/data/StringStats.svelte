<script lang="ts">
  import type { NumericStats, StringStats } from "./types";
  import HistChart from "$lib/components/viz/HistChart.svelte";
  import WordBarChart from "$lib/components/viz/WordBarChart.svelte";

  
  let { 
    stringData
  } = $props<{

    stringData: StringStats;
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
            <div class="font-bold text-primary-950">Stats</div>
          </div>
          <div class="flex flex-row items-center px-2">
            <div class="font-bold text-primary-800 pr-1">Distinct:</div>
            <div class="text-black">{stringData.distinct.count} ({stringData.distinct.percent}%)</div>
          </div>
          <div class="flex flex-row items-center px-2">
            <div class="font-bold text-primary-800 pr-1">Min Length:</div>
            <div class="text-black">{stringData.char_stats.min_length}</div>
          </div>
          <div class="flex flex-row items-center px-2">
            <div class="font-bold text-primary-800 pr-1">Max Length:</div>
            <div class="text-black">{stringData.char_stats.max_length}</div>
          </div>
          <div class="flex flex-row items-center px-2">
            <div class="font-bold text-primary-800 pr-1">Median Length:</div>
            <div class="text-black">{stringData.char_stats.median_length}</div>
          </div>
          <div class="flex flex-row items-center px-2">
            <div class="font-bold text-primary-800 pr-1">Mean Length:</div>
            <div class="text-black">{stringData.char_stats.mean_length}</div>
          </div>
        </div>
      </div>
  
    </div>
    <div class="col-span-1 xl:col-span-4 w-full h-[350px]">
  
      <div class="flex flex-row flex-wrap pb-1 items-center justify-between w-full">
        <div class="flex items-center justify-center">
          <div class="font-bold text-primary-950">Word Occurrence (Top 10)</div>
        </div>
        <button class="btn flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
          <div class="text-black">Reset Zoom</div>
        </button>
      </div>
  
      <div class="h-[320px]">
        <WordBarChart
          wordStats={stringData.word_stats}
          bind:resetZoom={resetZoom}
        />
      </div>
  
    </div>
  </div>