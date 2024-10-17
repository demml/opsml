
<script lang="ts">
    import Chart from 'chart.js/auto';
    import { Filler } from 'chart.js';
    import { onMount, onDestroy } from 'svelte';
    import ChartDataLabels from 'chartjs-plugin-datalabels';
    import 'chartjs-adapter-date-fns';
  
  
    export let data;
    export let options;
    export let type = 'bar';

    let ctx;
    let chartCanvas;
    let chart;
  
  
    Chart.register(ChartDataLabels);
    Chart.register(Filler);
  
    onMount(() => {
        ctx = chartCanvas.getContext('2d');
        chart = new Chart(ctx, {
        // @ts-ignore
        type: type,
        data: data,
        options: options,
        plugins: [ChartDataLabels],
        });

    });

   

  </script>
  
  <div class="h-48 mb-5">
    <div class="text-primary-500 font-bold pb-1">Word Statistics</div> 
    <canvas bind:this={chartCanvas}></canvas>
  </div>