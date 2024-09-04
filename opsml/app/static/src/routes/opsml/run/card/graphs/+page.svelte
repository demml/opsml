<script lang="ts">
    import {type RunGraph} from "$lib/scripts/types";
    import RunGraphChart from "$lib/card/run/RunGraph.svelte";
    import Fa from 'svelte-fa'
    import { faMagnifyingGlassMinus } from '@fortawesome/free-solid-svg-icons';
    import { RunCardStore } from "$routes/store";

    //import { buildXyChart, buildMultiXyChart} from "$lib/scripts/charts";

    // Alternatively, this is how to load Highcharts Stock. The Maps and Gantt
    // packages are similar.
    // import Highcharts from 'highcharts/highstock';

 
    let graphs: Map<string, RunGraph> | undefined;
    $: graphs = $RunCardStore.Graphs;

    function resetZoom(id) {
    // reset zoom
    // @ts-ignore
    window[id].resetZoom();
  }

</script>
<div class="flex min-h-screen">

  {#if graphs}
  <div class="grid grid-cols-1 md:grid-cols-2 w-full bg-white px-16 py-4 gap-4">

    {#each Array.from(Object.keys(graphs)) as key}

      <div class="pt-2 pb-10 rounded-2xl max-h-[450px] bg-surface-50 border-2 border-primary-500 shadow-md hover:border-secondary-500">

        <div class="flex justify-between">

          <div class="text-primary-500 text-lg font-bold pl-4 pt-1 pb-2">{key}</div>

          <div class="flex justify-end">

            <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white mr-2" on:click={() => resetZoom(key)}>
              <Fa class="h-3" icon={faMagnifyingGlassMinus}/>
              <header class="text-white text-xs">Reset Zoom</header>
            </button>
          </div>
        </div>  
        <RunGraphChart graph={graphs[key]} key={key} />
      </div>
      
    {/each}

  </div>
  
  {:else}
    <div class="text-center text-gray-500">No graphs available</div>
  {/if}




</div>
