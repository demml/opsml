<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import {type RunGraph} from "$lib/scripts/types";
  import {type ChartjsData} from "$lib/scripts/types";
  import { createRunGraphChart } from '$lib/scripts/runGraphChart';

	export let graph: RunGraph | undefined;
  export let key: string;
  
	let ctx;
	let chartCanvas;
  let chart;

  Chart.register(zoomPlugin);

  // get graph

  onMount(() => {

    if (!graph) {
      let chartData = createRunGraphChart(graph!) as ChartjsData;
      ctx = chartCanvas.getContext('2d');
      chart = new Chart(ctx, {

        // @ts-ignore
        type: chartData.type,
        data: chartData.data,
        options: chartData.options
      }
    );
    
   };

  return () => {
    chart.destroy();
  };

	});
</script>

<canvas bind:this={chartCanvas} id={key}></canvas>