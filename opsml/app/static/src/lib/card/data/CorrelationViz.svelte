
<script lang="ts">
    import Chart from 'chart.js/auto';
    import { Filler } from 'chart.js';
    import { onMount } from 'svelte';
    import ChartDataLabels from 'chartjs-plugin-datalabels';
    import 'chartjs-adapter-date-fns';
  
  
    export let data;
    export let options;
    export let type = 'bar';

    let ctx;
    let chartCanvas;
    let chart;
  
  
    Chart.unregister(ChartDataLabels);
    Chart.register(Filler);
  
    onMount(() => {
        ctx = chartCanvas.getContext('2d');
        chart = new Chart(ctx, {
        // @ts-ignore
        type: type,
        data: data,
        options: options,
        });

    });

   

  </script>
  
  <div class="h-48 mb-5 min-w-full">
    <div class="text-primary-500 font-bold pb-1">Feature Correlation</div> 
    <canvas bind:this={chartCanvas}></canvas>
  </div>