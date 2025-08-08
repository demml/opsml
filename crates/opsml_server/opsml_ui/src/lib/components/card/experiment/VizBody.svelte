
<script lang="ts">
  import type { BaseCard } from "$lib/components/home/types";
  import { onMount } from "svelte";
  import { getCardMetrics, getGroupedMetrics } from "./util";
  import type { Experiment, PlotType } from "./types";
  import Pill from "$lib/components/utils/Pill.svelte";
  import { type GroupedMetrics } from "./types";
  import Chart from "$lib/components/viz/Chart.svelte";
  import MetricTable from "./MetricTable.svelte";

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


<div class="flex flex-col h-full pb-4">

  <div class="flex flex-row flex-wrap gap-2 pb-3 items-center justify-between w-full">
    <div class="flex flex-row flex-wrap gap-2 items-center">
      {#each selectedMetrics as metric}
        <Pill key="metric" value={metric} textSize="text-sm"/>
      {/each}
    </div>

    <div class="flex flex-row gap-2">
      <button class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
          <div class="text-black">Reset Zoom</div>
      </button>
    </div>

  </div>

  {#key groupedMetrics}
    <div class="flex-1 overflow-auto mb-4"> <!-- Added wrapper with flex-1 -->
      <Chart 
        {groupedMetrics} 
          yLabel="Value" 
          {plotType}
          bind:resetZoom={resetZoom}
      />
    </div>
  {/key}

 


</div>