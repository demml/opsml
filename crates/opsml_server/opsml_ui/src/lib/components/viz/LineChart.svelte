
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import { createLineChart } from './linechart';
  import 'chartjs-adapter-date-fns';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import { Filler } from 'chart.js';

  let { 
    xValues, 
    yValues,
    labels,
    xLabel,
    yLabel,
    resetZoom = $bindable(),
  } = $props<{
    xValues: number[];
    yValues: number[][] | number[],
    labels: string[] | string,
    xLabel: string;
    yLabel: string;
    resetZoom: boolean;
  }>();


    let canvas: HTMLCanvasElement;
    let chart: Chart;

    Chart.register(zoomPlugin);
    Chart.register(annotationPlugin);
    Chart.register(Filler);

    function initChart() {

      const config = createLineChart(xValues, yValues, labels, xLabel, yLabel);
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

  <div class="w-full h-[400px]">
    <canvas bind:this={canvas}></canvas>
  </div>