<script lang="ts">
    import {type RunGraph} from "$lib/scripts/types";
    import RunGraphChart from "$lib/card/run/RunGraph.svelte";

    //import { buildXyChart, buildMultiXyChart} from "$lib/scripts/charts";

    // Alternatively, this is how to load Highcharts Stock. The Maps and Gantt
    // packages are similar.
    // import Highcharts from 'highcharts/highstock';

 
    /** @type {import('./$types').LayoutData} */
    export let data;

    let graphs: Map<string, RunGraph> | undefined;
    $: graphs = data.graphs

    

</script>
<div class="flex min-h-screen">

  {#if graphs}
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
      {#each Array.from(graphs.keys()) as key}
        <RunGraphChart graph={graphs.get(key)} key={key} />
      {/each}
    </div>
  {:else}

      <div class="text-center text-gray-500">No graphs available</div>
  {/if}



</div>
