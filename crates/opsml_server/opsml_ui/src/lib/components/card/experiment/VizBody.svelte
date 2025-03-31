
<script lang="ts">
  import type { BaseCard } from "$lib/components/home/types";
  import { onMount } from "svelte";
  import { getCardMetrics, getGroupedMetrics } from "./util";
  import type { Experiment, PlotType } from "./types";
  import Pill from "$lib/components/utils/Pill.svelte";
  import { type GroupedMetrics } from "./types";
  import LineChart from "$lib/components/viz/LineChart.svelte";

    let { 
      groupedMetrics,
      selectedMetrics,
      plotType,
    } = $props<{
      groupedMetrics: GroupedMetrics;
      selectedMetrics: string[];
      plotType: PlotType;
    }>();
  
    // state
    let resetZoom: boolean = $state(false);
  
    let resetZoomClicked = () => {
      resetZoom = !resetZoom;
    }


  </script>


<div class="flex flex-col h-full">
  <div class="items-center text-xl mr-2 font-bold text-primary-800">Recent Metrics</div>

  <div class="flex flex-row flex-wrap gap-2 pb-2 items-center justify-between w-full">
    <div class="flex flex-row flex-wrap gap-2 items-center">
      {#each selectedMetrics as metric}
        <Pill key="metric" value={metric} />
      {/each}
    </div>

    <button class="btn flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
      <div class="text-black">Reset Zoom</div>
    </button>
  </div>

  {#key groupedMetrics}
    <div class="flex-1"> <!-- Added wrapper with flex-1 -->
      <LineChart {groupedMetrics} yLabel="Value" bind:resetZoom={resetZoom}/>
    </div>
  {/key}

 


</div>