<script lang="ts">
    import {type RunGraph} from "$lib/scripts/types";
    import RunGraphChart from "$lib/card/run/RunGraph.svelte";
    import Fa from 'svelte-fa'
    import { faMagnifyingGlassMinus } from '@fortawesome/free-solid-svg-icons';
    import { RunCardStore } from "$routes/store";
    import logo from '$lib/images/opsml-logo.png';


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

{#if graphs}
<div class="flex min-h-screen">
  <div class="grid grid-cols-1 md:grid-cols-2 w-full bg-white px-16 py-4 gap-4" id="renderGraphs">

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
</div>  
  
{:else}
<div class="flex min-h-screen min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-white" id="notRendered">
  <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">

    <div class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5">

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-error-500">Oops!</h1>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <h2 class="text-primary-500 font-bold">No Graphs to Display</h2>
        <p class="mb-1 text-primary-500 text-center">
          No graphs found for this run.
        </p>

      </div>
      
    </div>
  </section>
</div>
{/if}
