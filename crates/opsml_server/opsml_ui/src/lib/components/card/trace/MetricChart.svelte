
<script lang="ts">
  import { Chart, type ChartConfiguration } from 'chart.js/auto';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import { onMount, onDestroy } from 'svelte';
  let { config, title } = $props<{ config: ChartConfiguration, title: String }>();

  let chart: Chart;
  let canvas: HTMLCanvasElement;
  Chart.register(zoomPlugin);
  Chart.register(annotationPlugin);

  let resetZoom: boolean = $state(false);

  let resetZoomClicked = () => {
    resetZoom = !resetZoom;
  }


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

    chart = new Chart(canvas, config);
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
  });

</script>


<div class="bg-white p-1 border-2 border-black rounded-lg shadow min-h-[12rem] h-full">
  <div class="flex flex-col h-full">
    <div class="flex flex-row flex-wrap gap-2 pb-2 items-center justify-between w-full px-2">
      <div class="items-center text-lg mr-2 font-bold text-primary-800">{title}</div>
      <button class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
        <div class="text-black">Reset Zoom</div>
      </button>
    </div>

    <div class="flex-1 min-h-0">
      <canvas bind:this={canvas}></canvas>
    </div>
  </div>
</div>