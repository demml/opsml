<script lang="ts">

  import { onMount, onDestroy } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import 'chartjs-adapter-date-fns';
  import { Filler } from 'chart.js';
  import type { WordStats } from '../card/data/types';
  import { createWordBarChart } from './wordChart';

  let { 
    wordStats,
    resetZoom = $bindable(),
  } = $props<{
    wordStats: WordStats;
    resetZoom: boolean;
  }>();

    let canvas: HTMLCanvasElement;
    let chart: Chart;

    Chart.register(zoomPlugin);
    Chart.register(Filler);

    function initChart() {
      let config =createWordBarChart(wordStats);
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