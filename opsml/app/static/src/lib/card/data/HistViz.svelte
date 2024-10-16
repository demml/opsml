
<script lang="ts">
    import Chart from 'chart.js/auto';
    import { Filler } from 'chart.js';
    import { onMount, onDestroy } from 'svelte';

    export let data;
    export let options;
    export let type = 'bar';

    let ctx;
    let chartCanvas;
    let chart;
  

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
      options: options
    });

    }

  
  </script>
  
  <div class="h-40 mb-5">
    <div class="text-primary-500 font-bold pb-1">Distribution</div> 
    <canvas bind:this={chartCanvas}></canvas>
  </div>