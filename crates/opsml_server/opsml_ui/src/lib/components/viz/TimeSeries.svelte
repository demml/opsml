
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import { createTimeSeriesChart } from './timeseries';
  import 'chartjs-adapter-date-fns';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import 'chartjs-adapter-date-fns';
  import { Filler } from 'chart.js';

  let { 
    timestamps, 
    values,
    baselineValue,
    label,
    yLabel,
    resetZoom = $bindable(),
  } = $props<{
    timestamps: string[];
    values: number[];
    baselineValue: number | undefined;
    label: string;
    yLabel: string;
    resetZoom: boolean;
  }>();


    let canvas: HTMLCanvasElement;
    let chart: Chart;

    Chart.register(zoomPlugin);
    Chart.register(annotationPlugin);
    Chart.register(Filler);

    function initChart() {

      const dates = timestamps.map((ts: string | number | Date) => new Date(ts));
      const config = createTimeSeriesChart(dates, values, baselineValue, label, yLabel);
      if (chart) {
        chart.destroy();
      }
      
      chart = new Chart(canvas, config);
    }


    // reset zoom effect
    $effect(() => {
      if (resetZoom && chart) {
        const zoomPlugin = chart.options.plugins?.zoom;
        if (zoomPlugin) {
          chart.resetZoom();
          resetZoom = false;
        }
      }
    });


    onMount(() => {
      if (chart) {
        chart.destroy();
      }

      initChart();
    });

    onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
  });
  </script>

  <div class="w-full h-[28rem]">
    <canvas bind:this={canvas}></canvas>
  </div>