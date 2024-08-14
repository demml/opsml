


<script lang="ts">
    import Chart from "chart.js/auto";
    import { onMount } from "svelte";

    export let name: string;
    export let chartData: any;
    export let options: any;
    export let type: any;

    let ctx;
    let chartCanvas;
    let chart;


  $: if (chart) {
    chart.data = chartData;
    chart.options = options;
    chart.type = type;

    chart.update();
  }

    
  onMount( async () => {
        ctx = chartCanvas.getContext('2d');
        chart = new Chart(ctx, {
            type: type,
            data: chartData,
            options: options
        }); 
    }
  );

</script>


<canvas bind:this={chartCanvas} id={name}></canvas>


