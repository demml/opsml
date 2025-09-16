<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";
  import type { BaseCard } from "$lib/components/home/types";
  import { Search } from "lucide-svelte";
  import { CircleDot } from 'lucide-svelte';
  import { List } from 'lucide-svelte';
  import ExperimentPill from "$lib/components/card/experiment/ExperimentPill.svelte";
  import { PlotType, type Experiment, type GroupedMetrics } from "$lib/components/card/experiment/types";
  import VizBody from "$lib/components/card/experiment/VizBody.svelte";
  import { getGroupedMetrics } from "$lib/components/card/experiment/util";
  import Dropdown from "$lib/components/utils/Dropdown.svelte";
  import ParameterTable from "$lib/components/card/experiment/ParameterTable.svelte";
  import { ChartNoAxesColumn } from 'lucide-svelte';
  import MetricTable from "$lib/components/card/experiment/MetricTable.svelte";
  import MetricComparisonTable from "$lib/components/card/experiment/MetricComparisonTable.svelte";

  let { data }: PageProps = $props();

  // base props
  let selectedMetrics: string[] = $state([]);
  let selectedExperiments: Experiment[]  = $state([]);
  let recentExperiments: Experiment[] = $state(data.recentExperiments);
  let groupedMetrics: GroupedMetrics | undefined = $state();
  let plotType: PlotType = $state(PlotType.Line);
  let plot: boolean = $state(false);

  // search setup
  let searchQuery = $state('');
  let availableEntities: string[] = $state(data.metricNames);
  let filteredEntities: string[] = $derived.by(() => {
    return availableEntities.filter((entity: string) => {
      return entity.toLowerCase().includes(searchQuery.toLowerCase());
    });
  });
  

  async function selectMetric(metricName: string) {
    // if the metric is already selected, remove it
    if (selectedMetrics.includes(metricName)) {
      selectedMetrics = selectedMetrics.filter((metric: string) => metric !== metricName);
    } else {
      // otherwise, add it to the selected metrics
      selectedMetrics = [...selectedMetrics, metricName];
    }
  }

  async function selectExperiment(selectedExperiment: Experiment) {
    // if the card version is already selected, remove it
    if (selectedExperiments.includes(selectedExperiment)) {
      selectedExperiments = selectedExperiments.filter((experiment: Experiment) => experiment !== selectedExperiment);
    } else {
      // otherwise, add it to the selected card versions
      selectedExperiments = [...selectedExperiments, selectedExperiment];
    }
  }

  async function plotMetrics() {
  
    // if selectedMetrics is empty, return
    if (selectedMetrics.length === 0) {
      alert('Please select at least one metric to plot.');
      return;
    }
    
    // add current experiment to selected experiments
    let currentExperiment: Experiment = {
      uid: data.metadata.uid,
      version: data.metadata.version,
    };

    let experimentsToPlot = [...selectedExperiments, currentExperiment];
    groupedMetrics = await getGroupedMetrics(experimentsToPlot, selectedMetrics);

    plot = true;
  }


  </script>
<div class="flex-1 mx-auto w-10/12 pb-10 flex justify-center overflow-auto px-4">
  <div class="grid grid-cols-1 lg:grid-cols-8 gap-4 w-full pt-4 ">

    <!-- Left Column-->
    <div class="col-span-1 lg:col-span-2 bg-surface-50 flex flex-col rounded-base border-black border-2 shadow h-[calc(100vh-200px)] overflow-y-auto">
      <!-- Top Section -->
      <div class="mb-4 sticky top-0 z-15 bg-surface-50 p-4">
        <div class="flex flex-row justify-between pb-2">
          <div class="flex flex-row">
            <div class="self-center" aria-label="Time Interval">
              <CircleDot color="#8059b6"/>
            </div>
            <header class="pl-2 text-primary-800 self-center font-bold">Search Metrics</header>
          </div>
          <div class="flex flex-row">
            <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2 self-center" onclick={plotMetrics}>Plot</button>
          </div>
        </div>

        <div class="flex flex-row pb-4">
          <div class="text-primary-800 self-center">Plot Type:</div>
          <div class="ml-2 self-center">
            <Dropdown  
              bind:selectedValue={plotType} 
              values={[PlotType.Bar, PlotType.Line]}
              width='w-32'
              py="py-1"
            />
          </div>
        </div>

        <div class="flex flex-row gap-1 items-center">
          <div class="mr-1">
            <Search color="#5948a3" />
          </div>  
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-1 border-black border-2 h-1/3"
            type="text"
            bind:value={searchQuery}
            placeholder="Search..."
          />
        </div>
      </div>
      <!-- Metrics and Experiments -->
      <div class="flex-1 p-4">
        <div class="mb-4">
          <div class="flex flex-row items-center mb-1 border-b-2 border-black">
            <List color="#8059b6"/>
            <header class="pl-2 text-primary-900 font-bold">Items</header>
          </div>
          <div class="space-y-2 flex flex-wrap pl-2 pt-4 pb-4 gap-1 overflow-y-scroll">
            <!-- Iterate of available entities -->
            {#each filteredEntities as entity}
          
              {#if selectedMetrics.includes(entity)}
                <button class="chip text-black bg-primary-500 border-black border-1 text-sm" onclick={() => selectMetric(entity)}>{entity}</button>
              {:else}
                <button class="chip bg-slate-100 border-primary-800 shadow-small shadow-hover-small border-2 text-primary-800 border-1 text-sm" onclick={() => selectMetric(entity)}>{entity}</button>
              {/if}
        
            {/each}
          </div>
        </div>

        <div class="mb-4">
          <div class="flex flex-row items-center mb-1 border-b-2 border-black">
            <List color="#8059b6"/>
            <header class="pl-2 text-primary-900 font-bold">Previous Versions</header>
          </div>
          <p class="pl-2 text-black text-sm">Select previous version to compare metrics</p>
          <div class="grid grid-cols-3 gap-2 pl-2 pt-4 pb-4 overflow-auto">
            {#each recentExperiments as experiment}
              {#if selectedExperiments.includes(experiment)}
                <ExperimentPill {experiment} active={true} setActive={selectExperiment}/>
              {:else}
                <ExperimentPill {experiment} active={false} setActive={selectExperiment}/>
              {/if}
            {/each}
          </div>
        </div>
      </div>
    </div>


    <!-- 2nd column -->
    <div class="col-span-1 lg:col-span-6 gap-4 w-full flex flex-col">

      <!-- Metrics plot -->
      <div class="bg-white p-4 border-2 border-black rounded-lg shadow mb-4 h-[calc(100vh-200px)] flex-shrink-0">

        <div class="flex flex-row">
          <div class="self-center" aria-label="Metric Plot">
            <ChartNoAxesColumn color="#8059b6"/>
          </div>
          <header class="pl-2 text-primary-800 text-lg self-center font-bold">Metrics</header>
        </div>

        {#if plot}
          {#if groupedMetrics}
            <VizBody {groupedMetrics} {selectedMetrics} {plotType} />
          {:else}
            <div class="flex items-center justify-center h-full text-gray-500 text-lg">
              No data available for selected metric
            </div>
          {/if}
        {:else}
          <div class="flex items-center justify-center h-full text-gray-500 text-lg">
            Select a metric to view data
          </div>
        {/if}
      </div>

      <!-- Metrics table-->
      {#if plot && groupedMetrics}
        <div class="bg-white p-4 border-2 border-black rounded-lg shadow mb-4 min-h-[6rem] max-h-[40rem] flex flex-col overflow-hidden">
          <div class="flex flex-row mb-4">
            <div class="self-center" aria-label="Metric Plot">
              <ChartNoAxesColumn color="#8059b6"/>
            </div>
            <header class="pl-2 text-primary-800 text-lg self-center font-bold">Metric Table</header>
          </div>
           {#if selectedExperiments.length > 0}
            <MetricComparisonTable {groupedMetrics} {selectedExperiments} currentVersion={data.metadata.version} />
          {:else}
            <MetricTable {groupedMetrics} />
          {/if}
        </div>
      {/if}

    </div>
  </div>
</div>