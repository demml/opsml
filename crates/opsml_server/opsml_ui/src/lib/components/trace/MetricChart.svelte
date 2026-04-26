
<script lang="ts">
  import { Chart, type ChartConfiguration } from 'chart.js/auto';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import { onMount, onDestroy } from 'svelte';
  import { themeStore } from '$lib/components/settings/theme.svelte';

  let { configFn, title } = $props<{ configFn: () => ChartConfiguration, title: String }>();

  let chart: Chart;
  let canvas: HTMLCanvasElement;
  let lastTriggerValue = 0;
  Chart.register(zoomPlugin);
  Chart.register(annotationPlugin);

  let resetZoomTrigger: number = $state(0);

  let resetZoomClicked = () => {
    resetZoomTrigger++;
  }

  function initChart() {
    if (chart) {
      chart.destroy();
    }
    chart = new Chart(canvas, configFn());
  }

  $effect(() => {
    if (resetZoomTrigger !== lastTriggerValue && chart) {
      chart.resetZoom();
      lastTriggerValue = resetZoomTrigger;
    }
  });

  // Re-render when chart configuration input changes.
  $effect(() => {
    configFn;
    title;
    if (chart && canvas) {
      initChart();
    }
  });

  // Re-render chart when theme changes
  $effect(() => {
    const _ = themeStore.resolved;
    if (chart && canvas) {
      initChart();
    }
  });

  onMount(() => {
    initChart();
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
  });

</script>


<div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden min-h-[12rem] h-full flex flex-col">
  <!-- Chart header -->
  <div class="flex items-center justify-between px-4 py-2.5 border-b-2 border-black bg-surface-50">
    <span class="text-sm font-black uppercase tracking-wide text-primary-800">{title}</span>
    <button
      onclick={() => resetZoomClicked()}
      class="text-xs font-bold px-2.5 py-1 bg-surface-50 border-2 border-black shadow-small shadow-hover-small rounded-base text-primary-800"
    >
      Reset Zoom
    </button>
  </div>

  <!-- Chart canvas -->
  <div class="flex-1 min-h-0 p-2">
    <canvas bind:this={canvas}></canvas>
  </div>
</div>
