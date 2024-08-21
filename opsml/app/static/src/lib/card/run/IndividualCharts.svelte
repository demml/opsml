<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
  import zoomPlugin from 'chartjs-plugin-zoom';

	export let data;
  export let type;
  export let options;
  
	let ctx;
	let chartCanvas;
  let chart;

  Chart.register(zoomPlugin);




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

  $: if (chart) {

    //check if chart.type is not undefined
    if (chart.type) {
      chart.destroy();
      ctx = chartCanvas.getContext('2d');
      chart = new Chart(ctx, {
        type: type,
        data: data,
        options: options
      });
    }
   
    chart.data = data;
    chart.type = type;
    chart.options = options;
    chart.update();

    window.metricChart = chart;

  }

</script>

<canvas bind:this={chartCanvas} id="metricChart"></canvas>