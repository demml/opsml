<script lang="ts">
    import Highcharts from "highcharts";
    // Alternatively, this is how to load Highcharts Stock. The Maps and Gantt
    // packages are similar.
    // import Highcharts from 'highcharts/highstock';

    // Load the exporting module.
    import Exporting from "highcharts/modules/exporting";
    // Initialize exporting module.
    Exporting(Highcharts);

    Highcharts.setOptions({
        colors: ['#04b78a', "#5e0fb7", "#bdbdbd", "#009adb", "#e74c3c", "#e73c3c", "#f2cc35"],
    });

    /** @type {import('./$types').LayoutData} */
    export let data;

    let graphs: Map<string, any>;
    $: graphs = data.graphs;



    

</script>

<div id="GraphContainer">

    <figure class="highcharts-figure">
        <div class="graph-child" id="graph"></div>
    </figure>
 
</div>
