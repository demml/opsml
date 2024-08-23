<script lang="ts">
    import { onMount } from "svelte";
    import {type Graph} from "$lib/scripts/types";
    import RunGraph from "$lib/card/run/RunGraph.svelte";
    //import { buildXyChart, buildMultiXyChart} from "$lib/scripts/charts";

    // Alternatively, this is how to load Highcharts Stock. The Maps and Gantt
    // packages are similar.
    // import Highcharts from 'highcharts/highstock';

 
    /** @type {import('./$types').LayoutData} */
    export let data;

    let graphs: Map<string, Graph> | undefined;
    $: graphs = data.graphs

    

</script>

{#if graphs}

  {#each Array.from(graphs.keys()) as key}
      <RunGraph graph={graphs.get(key)} key={key} />
  {/each}
 
{:else}
    <div class="text-center text-gray-500">No graphs available</div>
{/if}
