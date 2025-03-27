
<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import { createTimeSeriesChart } from './timeseries';
  import 'chartjs-adapter-date-fns';

  
  let { 
    timestamps = $bindable(), 
    values = $bindable(),
    label = $bindable(),
    yLabel = $bindable(),
  } = $props<{
    timestamps: string[];
    values: number[];
    label: string;
    yLabel: string;
  }>();




    let canvas: HTMLCanvasElement;
    let chart: Chart;

    function initChart() {
      const dates = timestamps.map((ts: string | number | Date) => new Date(ts));
      const config = createTimeSeriesChart(dates, values, label, yLabel);
      
      if (chart) {
        chart.destroy();
      }
      
      chart = new Chart(canvas, config);
    }

    $effect(() => {
      if (canvas && timestamps.length && values.length) {
        initChart();
      }
    });

    onMount(() => {
      if (timestamps.length && values.length) {
        initChart();
      }
    });
  </script>

  <div class="w-full h-[400px]">
    <canvas bind:this={canvas}></canvas>
  </div>