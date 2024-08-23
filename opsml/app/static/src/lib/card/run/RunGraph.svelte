<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import type RunGraph from "$lib/scripts/types";

	export let graph: RunGraph;
  export let key: string;
  //export let type;
  //export let options;
  
	let ctx;
	let chartCanvas;
  let chart;

  Chart.register(zoomPlugin);

  // get graph

  onMount(() => {
		  ctx = chartCanvas.getContext('2d');
		  chart = new Chart(ctx, {
				type: type,
				data: data,
        options: options
		});

    return () => {
      chart.destroy();
    };

	});
</script>