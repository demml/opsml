<script lang="ts">

  import { type ChartjsData, type DriftProfile, type FeatureDriftProfile, type FeatureDriftValues, TimeWindow  } from "$lib/scripts/types";
  import { getFeatureDriftValues, createDriftViz, rebuildDriftViz, generateTimestampsAndZeros } from "$lib/scripts/monitoring/utils";
  import logo from '$lib/images/opsml-green.ico';
  import { onMount } from 'svelte';
  import TimeChartDiv from '$lib/card/TimeChartDiv.svelte';
  import IndividualChart from "$lib/card/run/IndividualCharts.svelte";
  import scouter_logo from '$lib/images/scouter.svg';
  import Dropdown from "$lib/components/Dropdown.svelte";


  /** @type {import('./$types').LayoutData} */
  export let data;

  let driftProfile: DriftProfile;
  $: driftProfile = data.driftProfile;

  let targetFeature:FeatureDriftProfile;
  $: targetFeature = data.targetFeature;

  let features: string[];
  $: features = data.features;

  let driftVizData: ChartjsData;
  $: driftVizData = data.driftVizData;

  let featureDistVizData: ChartjsData;
  $: featureDistVizData = data.featureDistVizData;

  let timeWindow: string;
  $: timeWindow = data.timeWindow;

  let max_data_points: number;
  $: max_data_points = data.max_data_points;

  let name: string;
  $: name = data.name;

  let repository: string;
  $: repository = data.repository;

  let version: string;
  $: version = data.version;

  let vizId: string;
  $: vizId = "Drift values for " + targetFeature.id;

  let timeWindows: string[] = Object.values(TimeWindow);

  function debounce(func, time) {
    var time = time || 100; // 100 by default if no param
    var timer;
    return function(event){
        if(timer) clearTimeout(timer);
        timer = setTimeout(func, time, event);
    };
  }

function checkScreenSize() {

  if (window.innerWidth < 640) { // Check if screen width is less than 768px

    // Call your function for small screen size
    console.log("small screen");

  } else if (window.innerWidth < 768) { // Check if screen width is greater than or equal to 768px and less than 1024px

    // Call your function for medium screen size
    console.log("medium screen");

  } else if (window.innerWidth < 1024) {
    console.log("large screen");
  
  } else if (window.innerWidth < 1280) {
    console.log("xl screen");
    
  } else if (window.innerWidth < 1536) {
    console.log("2xl screen");

  } else { // Check if screen width is greater than or equal to 1024px
    // Call your function for large screen size
    console.log("large screen");
  }
}

window.addEventListener('resize', debounce(checkScreenSize, 400)); 



// Initial check on page load

checkScreenSize(); 

  function resetZoom(id) {
      // reset zoom
      // @ts-ignore
      window[id].resetZoom();
    }

  async function updateFeatureValues(feature:string) {

    if (feature === targetFeature.id) {
      return;
    }

    targetFeature = driftProfile.features[feature];
    let rebuiltViz = await rebuildDriftViz(repository, name, version, timeWindow, max_data_points, feature, targetFeature);

    driftVizData = rebuiltViz[0];
    featureDistVizData = rebuiltViz[1];

  }


  async function handleTimeWindowChange(event) {
    timeWindow = event.detail.selected;
    let rebuiltViz = await rebuildDriftViz(repository, name, version, timeWindow, max_data_points, targetFeature.id, targetFeature);
    driftVizData = rebuiltViz[0];
    featureDistVizData = rebuiltViz[1];
  }

  onMount (() => {
    console.log("loaded");
  });

</script>

{#if driftProfile}
<div class="flex min-h-screen">



  
  <div class="flex-col pt-4 px-8 w-full bg-white">

    <div class="flex justify-between">

      <div class="flex justify-between">
        <img alt="Scouter logo" class="h-9 mx-1 self-center" src={scouter_logo}>
        <div class="text-primary-500 text-xl font-bold py-1 self-center">Model Monitoring</div>
      </div>
    
      <div class="flex justify-end pr-8">

        <Dropdown 
        items={timeWindows}
        header={timeWindow}
        on:change={handleTimeWindowChange}
        />

      </div>
    </div> 


    <!-- Feature header -->
    <div class="flex flex-row items-center">
      <div class="m-1 text-darkpurple font-bold">Features:</div>
      <div class="flex flex-row flex-nowrap overflow-auto p-1 items-center">
        {#each features as feature}
          {#if feature === targetFeature.id}
            <button type="button" class="m-1 border border-darkpurple btn btn-sm bg-primary-400 hover:variant-soft-primary" on:click={() => updateFeatureValues(feature)}>
              <div class="text-white text-xs font-bold hover:text-darkpurple">{feature}</div>
            </button>
          {:else}
            <button type="button" class="m-1 border border-darkpurple btn btn-sm bg-surface-100 hover:variant-soft-primary" on:click={() => updateFeatureValues(feature)}>
              <div class="text-darkpurple text-xs font-bold">{feature}</div>
            </button>
          {/if}
        {/each}
      </div>
    </div>
  
    {#if driftVizData}
        <TimeChartDiv
          data={driftVizData.data}
          id={vizId}
          options={driftVizData.options}
          minHeight="min-h-[450px]"
        />
    {:else}
      <div class="flex justify-center items-center h-3/5">
        <p class="text-gray-400">No feature values found for the current time period</p>
      </div>
    {/if}
    <div class="pt-2">
      <div class="grid grid-cols-2 lg:grid-cols-6 gap-1">
        <div class="col-span-2 lg:col-span-4 min-h-[250px]  max-h-[250px] rounded-2xl border border-2 border-primary-500">01</div>
        <div class="col-span-2 lg:col-span-2  min-h-[250px] max-h-[250px] rounded-2xl border border-2 border-primary-500">
          <div class="flex flex-col">
            <div class="text-primary-500 text-lg font-bold pl-2 ">Feature Distribution</div>
            <div class="px-2 min-h-[200px]">
              <IndividualChart
                data={featureDistVizData.data}
                type="bar"
                options={featureDistVizData.options}
                id="featureChart"
                />
            </div>
          </div>
        </div>
      </div>

  
    </div>

  </div>

</div>
{:else}
<div class="flex min-h-screen min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-white" id="notLoaded">
  <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">

    <div class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5">

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-error-500">Oops!</h1>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <h2 class="text-primary-500 font-bold">No Drift Profile Detected</h2>
        <p class="mb-1 text-primary-500 text-center">
          A drift profile was not detected for this model
          If you'd like to enable monitoring, create a drift profile for this model.
        </p>

      </div>
      
    </div>
  </section>
</div>
{/if}