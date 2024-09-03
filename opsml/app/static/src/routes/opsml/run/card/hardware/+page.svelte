



<script lang="ts">

  import TimeChartDiv from "$lib/card/run/TimeChartDiv.svelte";
  import type { ParsedHardwareMetrics, HardwareCharts, RunCard } from "$lib/scripts/types";
  import { createHardwareCharts, getHardwareMetrics, parseHardwareMetrics } from "$lib/scripts/utils";
  import { onMount } from "svelte";
  import logo from '$lib/images/opsml-logo.png';

  /** @type {import('./$types').PageData} */
  export let data;

  let runcard: RunCard;
  $: runcard = data.metadata;

  let parsedMetrics: ParsedHardwareMetrics;
  $: parsedMetrics = data.parsedMetrics; 

  let charts: HardwareCharts | undefined;
  $: charts = undefined;

  onMount (() => {
    if (parsedMetrics) {
      charts = createHardwareCharts(parsedMetrics);
    }
  });

  async function refresh() {
    let metrics = await getHardwareMetrics(runcard.uid);

    if (metrics.metrics.length > 0) {
      parsedMetrics = parseHardwareMetrics(metrics.metrics);
      charts = createHardwareCharts(parsedMetrics);
    }
  
  }


</script>

{#if charts}
<div class="flex min-h-screen">


  <div class="flex flex-col w-full">
    <div class="flex flex-col w-full">
      <div class="mx-10 pt-4 border-b-2 border-gray-400">
        <div class="flex flex-row items-center justify-between">
          <header class="text-darkpurple text-lg font-bold">CPU Metrics</header>
          <button type="button" class="btn btn-sm bg-darkpurple text-white justify-end mb-2" on:click={() => refresh()}>Refresh</button>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 w-full bg-white px-10 py-4 gap-4">

        <TimeChartDiv data={charts.cpu_overall.data} id="CPU Utilization (Overall)" options={charts.cpu_overall.options} />

        {#if charts.cpu_per_core }
          <TimeChartDiv data={charts.cpu_per_core.data} id="CPU Utilization (Per Core)" options={charts.cpu_per_core.options} />
        {/if}
      
      </div>
    </div>

    <div class="flex flex-col w-full">
      <div class="mx-10 pt-4 border-b-2 border-gray-400">
        <header class="text-darkpurple text-lg font-bold">Memory Metrics</header>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 w-full bg-white px-10 py-4 gap-4">

        <TimeChartDiv data={charts.memory.data} id="Memory" options={charts.memory.options} />
      
      </div>
    </div>

    <div class="flex flex-col w-full">
      <div class="mx-10 pt-4 border-b-2 border-gray-400">
        <header class="text-darkpurple text-lg font-bold">Network Metrics</header>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 w-full bg-white px-10 py-4 gap-4">

        <TimeChartDiv data={charts.network_tx.data} id="Transmitted Bytes" options={charts.network_tx.options} />
        <TimeChartDiv data={charts.network_rx.data} id="Received Bytes" options={charts.network_rx.options} />
      
      </div>
    </div>

    {#if charts.gpu_overall}

      <div class="flex flex-col w-full">
        <div class="mx-10 pt-4 border-b-2 border-gray-400">
          <header class="text-darkpurple text-lg font-bold">GPU Metrics</header>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 w-full bg-white px-10 py-4 gap-4">

          <TimeChartDiv data={charts.gpu_overall.data} id="Transmitted Bytes" options={charts.gpu_overall.options} />

          {#if charts.gpu_per_core}
            <TimeChartDiv data={charts.gpu_per_core.data} id="Received Bytes" options={charts.gpu_per_core.options} />
          {/if}
        
        </div>
      </div>


    {/if}

  </div>
 </div>
  

  {:else}
  <div class="flex min-h-screen min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-white">
    <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">
  
      <div class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5">
  
        <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
        <h1 class="pt-1 text-center text-3xl font-bold text-error-500">Oops!</h1>
  
        <div class="mb-8 grid grid-cols-1 gap-3">
          <h2 class="text-primary-500 font-bold">No Hardware Metrics</h2>
          <p class="mb-1 text-primary-500 text-center">
            No hardware metrics found for this run.
            This may be expected if using an older version of OpsML or logging was turned off for the run.
          </p>
  
        </div>
        
      </div>
    </section>
  </div>
  {/if}
