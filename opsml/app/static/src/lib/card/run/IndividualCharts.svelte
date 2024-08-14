<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';

	export let data;
  export let type;
  export let options;
  
	let ctx;
	let chartCanvas;
  let chart;


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
    chart.data = data;
    chart.type = type;
    chart.options = options;
    chart.update();
  }

</script>

<canvas bind:this={chartCanvas} id="myChart"></canvas>