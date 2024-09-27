<script lang="ts">

  import { type ChartjsData, type DriftProfile, type FeatureDriftProfile, type FeatureDriftValues, TimeWindow, type MonitorAlerts , ProfileType } from "$lib/scripts/types";
  import { getFeatureDriftValues, createDriftViz, rebuildDriftViz, generateTimestampsAndZeros } from "$lib/scripts/monitoring/utils";
  import logo from '$lib/images/opsml-green.ico';
  import { onMount } from 'svelte';
  import TimeChartDiv from '$lib/card/TimeChartDiv.svelte';
  import IndividualChart from "$lib/card/run/IndividualCharts.svelte";
  import scouter_logo from '$lib/images/scouter.svg';
  import Dropdown from "$lib/components/Dropdown.svelte";
  import AlertDiv from "$lib/card/monitoring/Alerts.svelte";
  import SPCProfile from "$lib/card/monitoring/SPCProfile.svelte";
  import SpcStats from "$lib/card/monitoring/SPCStats.svelte";


  /** @type {import('./$types').LayoutData} */
  export let data;

  let driftProfiles: Map<ProfileType, DriftProfile>;
  $: driftProfiles = data.driftProfiles;

  let targetFeature:FeatureDriftProfile;
  $: targetFeature = data.targetFeature;

  let features: string[];
  $: features = data.features;

  let driftVizData: ChartjsData;
  $: driftVizData = data.driftVizData;

  let featureDistVizData: ChartjsData;
  $: featureDistVizData = data.featureDistVizData;

  let alertMetricVizData: ChartjsData;
  $: alertMetricVizData = data.alertMetricVizData;

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

  let driftVizId: string;
  $: driftVizId = "Drift values for " + targetFeature.id;

  let alertMeticsId: string;
  $: alertMeticsId = 'Alert Metrics';

  let alerts: MonitorAlerts;
  $: alerts = data.alerts;

  let showProfile: boolean;
  $: showProfile = data.showProfile;

  let profileType: ProfileType;
  $: profileType = data.profileType;

  let timeWindows: string[] = Object.values(TimeWindow);

  function debounce(func, time) {
    var time = time || 100; // 100 by default if no param
    var timer;
    return function(event){
        if(timer) clearTimeout(timer);
        timer = setTimeout(func, time, event);
    };
  }

async function checkScreenSize() {

  if (window.innerWidth < 640) { // Check if screen width is less than 768px
    max_data_points = 100;

  } else if (window.innerWidth < 768) { // Check if screen width is greater than or equal to 768px and less than 1024px

    max_data_points = 250;

  } else if (window.innerWidth < 1024) {
    max_data_points = 1000;
  
  } else if (window.innerWidth < 1280) {
    max_data_points = 2500;
    
  } else if (window.innerWidth < 1536) {
    max_data_points = 5000;

  } else { // Check if screen width is greater than or equal to 1024px
    // Call your function for large screen size
    max_data_points = 5000;
  }
  let rebuiltViz = await rebuildDriftViz(repository, name, version, timeWindow, max_data_points, targetFeature.id, targetFeature);

  driftVizData = rebuiltViz[0];
  featureDistVizData = rebuiltViz[1];

}

function toggleProfile() {
  showProfile = !showProfile;
}


  function resetZoom(id) {
      // reset zoom
      // @ts-ignore
      window[id].resetZoom();
    }

  async function updateFeatureValues(feature:string) {

    if (feature === targetFeature.id) {
      return;
    }

    targetFeature = driftProfiles[profileType].features[feature];
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
    window.addEventListener('resize', debounce(checkScreenSize, 400)); 
  });

  function handleUpdate(event) {
    showProfile = event.detail.showProfile;
    driftProfiles[profileType].config = event.detail.updatedDriftConfig;
  }

  function handleHide(event) {
    showProfile = event.detail.showProfile;
  }

  function handleFeatureUpdate(event) {
  
    updateFeatureValues(event.detail.feature);
  }

</script>

<main>
  {#if driftProfiles}
  <div class="flex min-h-screen overflow-x-scroll bg-white">
  
      <div class="flex-col pt-4 w-full px-8">
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
        
        <!-- Profile header -->
        <div class="flex flex-row items-center">
          <div class="m-1 text-darkpurple font-bold">Drift Configuration:</div>
            <div class="flex flex-row flex-nowrap overflow-auto p-1 items-center">

              {#if showProfile}
                <button type="button" class="m-1 border border-darkpurple btn btn-sm bg-primary-400 hover:variant-soft-primary" on:click={toggleProfile}>
                  <div class="text-white text-xs font-bold hover:text-darkpurple">Hide</div>
                </button>
              {:else}
                <button type="button" class="m-1 border border-darkpurple btn btn-sm bg-surface-100 hover:variant-soft-primary" on:click={toggleProfile}>
                  <div class="text-darkpurple text-xs font-bold">Show</div>
                </button>
              {/if}
            </div>
        </div>
        
        <!-- Feature header -->
        <div class="flex flex-row items-center overflow-auto">
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
      

        <!-- Drift Viz -->
        {#if driftVizData}
        <div class="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-y-1 lg:gap-x-2">
          <div class="col-span-2 xl:col-span-3">
            <TimeChartDiv
              data={driftVizData.data}
              id={driftVizId}
              options={driftVizData.options}
              minHeight="min-h-[350px] lg:min-h-[500px]"
            />
          </div>
          <div class="col-span-1">

            <SpcStats
              feature_profile={targetFeature}
              featureDistVizData={featureDistVizData}
            />

  
          </div>
        </div>
        {:else}
          <div class="flex justify-center items-center h-4/5">
            <p class="text-gray-400">No feature values found for the current time period</p>
          </div>
        {/if}
      </div>
    </div>


 
  
  {/if}
</main>