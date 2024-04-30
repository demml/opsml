<script lang="ts">
    import { onMount } from "svelte";
    import {type Graph} from "$lib/scripts/types";
    import { buildXyChart, buildMultiXyChart} from "$lib/scripts/charts";

    // Alternatively, this is how to load Highcharts Stock. The Maps and Gantt
    // packages are similar.
    // import Highcharts from 'highcharts/highstock';

 
    /** @type {import('./$types').LayoutData} */
    export let data;

    let graphs: Map<string, Graph>;
    $: graphs = data.graphs;

    onMount(() => {
        Object.keys(graphs).forEach((graph) => {
            if (graphs[graph].graph_type === "single") {
                buildXyChart(graphs[graph]);
            } else {
                buildMultiXyChart(graphs[graph]);
            }
        });
    });

    

</script>

<div class="pl-4 pr-4 md:pl-12 md:pr-12">
    <figure class="highcharts-figure">
        <div class="grid grid-cols-3 gap-4">
            {#each Object.keys(graphs) as graph}
                <div class="col-span-3 md:col-span-1">
                    <div id='graph_{graph}'></div>
                </div>
            {/each}
        </div>
    </figure>
</div>
