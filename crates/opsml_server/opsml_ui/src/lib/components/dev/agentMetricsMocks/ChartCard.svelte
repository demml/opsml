<script lang="ts">
  import { Chart, type ChartConfiguration } from 'chart.js/auto';
  import 'chartjs-adapter-date-fns';
  import { onDestroy } from 'svelte';
  import { themeStore } from '$lib/components/settings/theme.svelte';

  let {
    configFn,
    title,
    subtitle = '',
    height = 'h-56'
  }: {
    configFn: () => ChartConfiguration;
    title: string;
    subtitle?: string;
    height?: string;
  } = $props();

  let canvas: HTMLCanvasElement;
  let chart: Chart | undefined;

  function initChart() {
    if (chart) chart.destroy();
    chart = new Chart(canvas, configFn());
  }

  $effect(() => {
    configFn;
    title;
    themeStore.resolved;
    if (canvas) initChart();
  });

  onDestroy(() => chart?.destroy());
</script>

<div class="rounded-base border-2 border-black shadow bg-surface-50 flex flex-col overflow-hidden">
  <div class="flex items-baseline justify-between px-4 py-2.5 border-b-2 border-black bg-surface-100">
    <span class="text-sm font-black uppercase tracking-wide text-primary-800">{title}</span>
    {#if subtitle}
      <span class="text-xs font-mono text-gray-700">{subtitle}</span>
    {/if}
  </div>
  <div class="flex-1 p-3 {height}">
    <canvas bind:this={canvas}></canvas>
  </div>
</div>
