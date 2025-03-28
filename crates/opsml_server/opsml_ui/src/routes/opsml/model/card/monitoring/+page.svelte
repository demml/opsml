<script lang="ts">
  import type { BinnedDriftMap, MetricData, SpcDriftFeature, BinnedPsiMetric, BinnedCustomMetric, BinnedCustomMetricStats  } from '$lib/components/monitoring/types';
  import { DriftType } from '$lib/components/monitoring/types';
  import type { DriftProfile, DriftProfileResponse } from '$lib/components/monitoring/util';
  import type { PageProps } from './$types';
  import { TimeInterval } from '$lib/components/monitoring/types';
  import VizBody from '$lib/components/monitoring/VizBody.svelte';
  import Header from '$lib/components/monitoring/Header.svelte';
  import { getMaxDataPoints, debounce } from '$lib/utils';
  import { getLatestMetricsExample, getCurrentMetricData } from '$lib/components/monitoring/util';
  import { onMount, onDestroy } from 'svelte';
  import { getProfileFeatures, getProfileConfig, type DriftConfigType } from '$lib/components/monitoring/util';

 
  let { data }: PageProps = $props();

  let profiles: DriftProfileResponse = data.profiles;

  // Props
  let currentName: string = $state(data.currentName);
  let currentNames: string[] = $state(data.currentNames);
  let currentDriftType: DriftType = $state(data.currentDriftType);
  let currentProfile: DriftProfile = $state(data.currentProfile);
  let latestMetrics: BinnedDriftMap = $state(data.latestMetrics);
  let currentMetricData: MetricData = $state(data.currentMetricData);
  let currentMaxDataPoints: number = $state(data.maxDataPoints);
  let currentConfig: DriftConfigType = $state(data.currentConfig);

  // Vars
  let drift_types: DriftType[] = data.keys;
  let currentTimeInterval: TimeInterval = $state(TimeInterval.SixHours);
  
  let chartState = $derived({
    driftType: currentDriftType,
    name: currentName,
    timeInterval: currentTimeInterval,
    metricData: currentMetricData,
    timestamp: Date.now() // Force updates
  });

 

  // check current screen size
  // if screen size has changed, call getScreenSize()
  // update currentScreenSize
  // call getLatestMetricsExample() with new screen size

  async function checkScreenSize() {
    const newMaxDataPoints = getMaxDataPoints();
      if (newMaxDataPoints !== currentMaxDataPoints) {
        currentMaxDataPoints = newMaxDataPoints;
        latestMetrics = await getLatestMetricsExample(
          profiles,
          currentTimeInterval,
          currentMaxDataPoints  
        );

        currentMetricData = getCurrentMetricData(
            latestMetrics,
            currentDriftType,
            currentName
          );
      }
    }

  const debouncedCheckScreenSize = debounce(checkScreenSize, 400);

  onMount(() => {
    window.addEventListener('resize', debouncedCheckScreenSize);
  });

  onDestroy(() => {
    window.removeEventListener('resize', debouncedCheckScreenSize);
  });

  function handleDriftTypeChange(drift_type: DriftType) {
    currentDriftType = drift_type;
    currentProfile = profiles[drift_type];
    currentNames = getProfileFeatures(currentDriftType, currentProfile);
    currentName = currentNames[0];
    currentConfig = getProfileConfig(currentDriftType, currentProfile);
    currentMetricData = getCurrentMetricData(
      latestMetrics,
      currentDriftType,
      currentName
    );
  }

  function handleNameChange(name: string) {
    currentName = name;
    currentMetricData = getCurrentMetricData(
      latestMetrics,
      currentDriftType,
      currentName
    );
  }

  async function handleTimeChange(timeInterval: TimeInterval) {
    currentTimeInterval = timeInterval;
    latestMetrics = await getLatestMetricsExample(
          profiles,
          currentTimeInterval,
          currentMaxDataPoints  
        );

    currentMetricData = getCurrentMetricData(
        latestMetrics,
        currentDriftType,
        currentName
      );
  }


  


 </script>
 
 <div class="mx-auto w-11/12 pb-10 flex justify-center">
  <div class="grid grid-cols-1 gap-4 w-full pt-4">

    <!--Create 3 row grid. First row contains 2 columns, 2nd row contains 1 column, 3rd row contains 1 col-->
    <div class="h-fit">
      <Header
            availableDriftTypes={drift_types}
            currentDriftType={currentDriftType}
            bind:currentTimeInterval={currentTimeInterval}
            bind:currentName={currentName}
            currentNames={currentNames}
            currentConfig={currentConfig}
            currentProfile={currentProfile}
            {handleDriftTypeChange}
            {handleNameChange}
            {handleTimeChange}
      /> 
    </div>

    <!-- Row 2: 1 column -->
    <div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
      
      {#if currentName && latestMetrics}
        {#if currentMetricData}
          <VizBody
            metricData={currentMetricData}
            currentDriftType={currentDriftType}
            currentName={currentName}
            currentTimeInterval={currentTimeInterval}
            currentConfig={currentConfig}
            currentProfile={currentProfile}
          />
        {:else}
          <div class="flex items-center justify-center h-full text-gray-500">
            No data available for selected metric
          </div>
        {/if}
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
          Select a metric to view data
        </div>
      {/if}
    </div>

    <!-- Row 3: 1 column -->
    <div class="bg-white p-4 rounded-lg shadow h-[400px]">
      <h2 class="text-lg font-semibold mb-2">Row 3</h2>
      <div class="text-black">Content for row 3</div>
    </div>




  </div>
 </div>
 