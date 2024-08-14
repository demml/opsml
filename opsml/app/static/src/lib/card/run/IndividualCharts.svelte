<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';

	export let data;
  export let type;
  export let options;
  
	let ctx;
	let chartCanvas;

	onMount(() => {
		  ctx = chartCanvas.getContext('2d');
			var chart = new Chart(ctx, {
				type: type,
				data: data,
        options: options
		});

	});

</script>

<canvas bind:this={chartCanvas} id="myChart"></canvas>