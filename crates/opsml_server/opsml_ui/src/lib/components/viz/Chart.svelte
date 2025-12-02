
<script lang="ts">
  // This chart supports both bar and line charts
  import { onMount, onDestroy } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import 'chartjs-adapter-date-fns';
  import { Filler } from 'chart.js';
  import { PlotType, type GroupedMetrics } from '../card/experiment/types';
  import { createLineChart, createGroupedBarChart } from './chart';

  let {
    groupedMetrics,
    yLabel,
    plotType,
    resetZoomTrigger = $bindable(),
  } = $props<{
    groupedMetrics: GroupedMetrics;
    yLabel: string;
    plotType: PlotType;
    resetZoomTrigger: number;
  }>();


    let canvas: HTMLCanvasElement;
    let chart: Chart;
    let lastTriggerValue = 0;

    Chart.register(zoomPlugin);
    Chart.register(annotationPlugin);
    Chart.register(Filler);

    function initChart() {
      let config = plotType === PlotType.Line
      ? createLineChart(groupedMetrics, yLabel)
      : createGroupedBarChart(groupedMetrics, yLabel);

      if (chart) {
        chart.destroy();
      }

      chart = new Chart(canvas, config);
    }


    // reset zoom effect
    $effect(() => {
      if (resetZoomTrigger !== lastTriggerValue && chart) {
        chart.resetZoom();
        lastTriggerValue = resetZoomTrigger;
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