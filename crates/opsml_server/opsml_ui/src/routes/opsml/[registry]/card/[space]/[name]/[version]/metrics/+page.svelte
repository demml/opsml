<script lang="ts">

  import type { PageProps } from './$types';
  import { Search, CircleDot, List, ChartNoAxesColumn } from "lucide-svelte";
  import { ServerPaths } from "$lib/components/api/routes";
  import ExperimentPill from "$lib/components/card/experiment/ExperimentPill.svelte";
  import { PlotType, type Experiment, type GroupedMetrics } from "$lib/components/card/experiment/types";
  import VizBody from "$lib/components/card/experiment/VizBody.svelte";
  import { createInternalApiClient} from "$lib/api/internalClient";
  import Dropdown from "$lib/components/utils/Dropdown.svelte";
  import MetricTable from "$lib/components/card/experiment/MetricTable.svelte";
  import MetricComparisonTable from "$lib/components/card/experiment/MetricComparisonTable.svelte";
  import MultiComboBoxDropDown from '$lib/components/utils/MultiComboBoxDropDown.svelte';

  let { data }: PageProps = $props();

  // base props
  let selectedMetrics: string[] = $state([]);
  let groupedMetrics: GroupedMetrics | undefined = $state();


  let selectedExperiments: Experiment[]  = $state([]);
  let recentExperiments: Experiment[] = $state(data.recentExperiments);

  let selectedExperimentVersions: string[] = $state([]);
  let recentExperimentVersions: string[] = $derived.by(() => {
    return recentExperiments.map((experiment: Experiment) => experiment.version);
  });
 
  let plotType: PlotType = $state(PlotType.Line);
  let plot: boolean = $state(false);

  let availableEntities: string[] = $state(data.metricNames);


  // effect to update selectedExperiments when selectedExperimentVersions changes
  $effect(() => {
    selectedExperiments = recentExperiments.filter((experiment: Experiment) => selectedExperimentVersions.includes(experiment.version));
  });

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
    let resp = await createInternalApiClient(fetch).post(ServerPaths.EXPERIMENT_GROUPED_METRICS, {
      experiments: experimentsToPlot,
      selectedMetrics
    });

    groupedMetrics = (await resp.json() as GroupedMetrics);

    plot = true;
  }


  </script>
<div class="mx-auto max-w-8xl pb-8 px-4">
  <div class="grid grid-cols-1 lg:grid-cols-6 gap-4 w-full pt-4 ">

    <!-- Left Column-->
    <div class="col-span-1 flex-1 lg:col-span-1 mb-4 text-black flex flex-col w-full relative">

      <div class="bg-white rounded-base border-black border-2 shadow overflow-y-auto w-full">
      <!-- Top Section -->
        <div class="mb-2 p-4">
          <div class="flex flex-row justify-between pb-4">
            <div class="flex flex-row">
              <div class="self-center" aria-label="Time Interval">
                <CircleDot color="#8059b6"/>
              </div>
              <header class="pl-2 text-primary-800 self-center font-bold text-lg">Search Metrics</header>
            </div>
            <div class="flex flex-row">
              <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2 self-center" onclick={plotMetrics}>Plot</button>
            </div>
          </div>

          <div class="flex flex-row pb-5">
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

          <div class="flex justify-self-start gap-1 w-full">
            <MultiComboBoxDropDown
              boxId="metric-search-input"
              label="Metrics"
              bind:filteredItems={selectedMetrics}
              availableOptions={availableEntities}
            />
          </div>
          <div class="flex justify-self-start gap-1 w-full">
            <MultiComboBoxDropDown
              boxId="experiment-search-input"
              label="Experiments"
              bind:filteredItems={selectedExperimentVersions}
              availableOptions={recentExperimentVersions}
            />
          </div>
        </div>
      </div>  
    </div>


    <!-- 2nd column -->
    <div class="col-span-1 lg:col-span-5 flex flex-col gap-4">

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