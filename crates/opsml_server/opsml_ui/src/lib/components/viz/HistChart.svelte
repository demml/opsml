
<script lang="ts">
  // This chart supports both bar and line charts
  import { onMount, onDestroy } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import 'chartjs-adapter-date-fns';
  import { Filler } from 'chart.js';
  import type { Histogram } from '../card/data/types';
  import { createHistogramViz } from './hist';
  import { themeStore } from '$lib/components/settings/theme.svelte';

  let {
    histData,
    resetZoomTrigger= $bindable(),
  } = $props<{
    histData: Histogram;
    resetZoomTrigger: number;
  }>();


    let canvas: HTMLCanvasElement;
    let chart: Chart;
    let lastTriggerValue = 0;

    Chart.register(zoomPlugin);
    Chart.register(Filler);


    function initChart() {
      let config = createHistogramViz(histData);

      if (chart) {
        chart.destroy();
      }

      chart = new Chart(canvas, config);
    }



    $effect(() => {
      if (resetZoomTrigger !== lastTriggerValue && chart) {
        chart.resetZoom();
        lastTriggerValue = resetZoomTrigger;
      }
    });

    // Re-render on theme change
    $effect(() => {
      const _ = themeStore.resolved;
      if (chart && canvas) {
        initChart();
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