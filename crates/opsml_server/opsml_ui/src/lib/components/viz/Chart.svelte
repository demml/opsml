
<script lang="ts">
  // This chart supports both bar and line charts
  import { onMount, onDestroy } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import 'chartjs-adapter-date-fns';
  import { Filler } from 'chart.js';
  import { PlotType, type GroupedMetrics } from '../card/experiment/types';
  import { createLineChart, createBarChart } from './chart';

  let { 
    groupedMetrics,
    yLabel,
    plotType,
    resetZoom = $bindable(),
  } = $props<{
    groupedMetrics: GroupedMetrics;
    yLabel: string;
    plotType: PlotType;
    resetZoom: boolean;
  }>();


    let canvas: HTMLCanvasElement;
    let chart: Chart;

    Chart.register(zoomPlugin);
    Chart.register(annotationPlugin);
    Chart.register(Filler);

    function initChart() {
      console.log('Plotting chart with type:', plotType);
      let config = plotType === PlotType.Line 
      ? createLineChart(groupedMetrics, yLabel)
      : createBarChart(groupedMetrics, yLabel);
  
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

  <div class="w-full h-full">
    <canvas bind:this={canvas}></canvas>
  </div>