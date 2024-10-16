
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
        createChart();
        
        return () => {
        if (chart) {
            chart.destroy();
            }
        };
    });

    onDestroy(() => {
      if (chart) {
        chart.destroy();
      }
    });

  
    function createChart() {
    ctx = chartCanvas.getContext('2d');
    chart = new Chart(ctx, {
      // @ts-ignore
      type: type,
      data: data,
      options: options,
      plugins: [ChartDataLabels],
    });

    }

    $: if (chart && data) {
      chart.destroy();
      createChart();
    }

  </script>
  
  <div class="min-h-40 max-h-48 mb-5 max-w-sm">
    <div class="text-primary-500 font-bold pb-1">Word Statistics</div> 
    <canvas bind:this={chartCanvas}></canvas>
  </div>