<script lang="ts">
  import type { BinnedDriftMap, MetricData  } from '$lib/components/card/monitoring/types';
  import { DriftType } from '$lib/components/card/monitoring/types';
  import type { DriftProfile, DriftProfileResponse, UiProfile } from '$lib/components/card/monitoring/util';
  import type { PageProps } from './$types';
  import { TimeInterval } from '$lib/components/card/monitoring/types';
  import VizBody from '$lib/components/card/monitoring/VizBody.svelte';
  import Header from '$lib/components/card/monitoring/Header.svelte';
  import { getMaxDataPoints, debounce } from '$lib/utils';
  import { getLatestMetrics, getCurrentMetricData } from '$lib/components/card/monitoring/util';
  import { onMount, onDestroy } from 'svelte';
  import { getProfileFeatures, getProfileConfig, type DriftConfigType } from '$lib/components/card/monitoring/util';
  import type { Alert } from '$lib/components/card/monitoring/alert/types';
  import { getDriftAlerts, acknowledgeAlert } from '$lib/components/card/monitoring/alert/utils';
  import AlertTable from '$lib/components/card/monitoring/alert/AlertTable.svelte';

 
  let { data }: PageProps = $props();

  let profiles: DriftProfileResponse = data.profiles;
  
  // Props
  let currentName: string = $state(data.currentName);
  let currentNames: string[] = $state(data.currentNames);
  let currentDriftType: DriftType = $state(data.currentDriftType);
  let currentProfile: UiProfile = $state(data.currentProfile);
  let latestMetrics: BinnedDriftMap = $state(data.latestMetrics);
  let currentMetricData: MetricData = $state(data.currentMetricData);
  let currentMaxDataPoints: number = $state(data.maxDataPoints);
  let currentConfig: DriftConfigType = $state(data.currentConfig);
  let currentAlerts: Alert[] = $state(data.currentAlerts);
  let uid: string = $state(data.metadata.uid);
  let registry = $state(data.registry);

  // Vars
  let drift_types: DriftType[] = data.keys;
  let currentTimeInterval: TimeInterval = $state(TimeInterval.SixHours);

  // check current screen size
  // if screen size has changed, call getScreenSize()
  // update currentScreenSize
  // call getLatestMetricsExample() with new screen size

  async function checkScreenSize() {
    const newMaxDataPoints = getMaxDataPoints();
      if (newMaxDataPoints !== currentMaxDataPoints) {
        currentMaxDataPoints = newMaxDataPoints;
        latestMetrics = await getLatestMetrics(
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
    currentProfile= profiles[drift_type];

    currentNames = getProfileFeatures(currentDriftType, currentProfile.profile);
    currentName = currentNames[0];

    currentConfig = getProfileConfig(currentDriftType, currentProfile.profile);


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
    latestMetrics = await getLatestMetrics(
          profiles,
          currentTimeInterval,
          currentMaxDataPoints  
        );

    currentMetricData = getCurrentMetricData(
        latestMetrics,
        currentDriftType,
        currentName
      );

    currentAlerts = await getDriftAlerts(
      currentConfig.space,
      currentConfig.name,
      currentConfig.version,
      currentTimeInterval,
      true
    );
  }

  async function updateAlert(id: number, space: string) {
    // Call API to acknowledge alert
    let updated = await acknowledgeAlert(id, space);

    if (updated) {
      currentAlerts = await getDriftAlerts(
          currentConfig.space,
          currentConfig.name,
          currentConfig.version,
          currentTimeInterval,
          true
        );


      }
     
  }


 </script>
 
 <div class="flex-1 mx-auto w-9/12 pb-10 flex justify-center overflow-auto px-4">
  <div class="grid grid-cols-1 gap-4 w-full pt-4">

    <!-- For my memory :) -->
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
            {uid}
            {registry}
      /> 
    </div>

    <!-- Row 2: 1 column -->
    <div class="bg-white p-2 border-2 border-black rounded-lg shadow min-h-[30rem]">
      
      {#if currentName && latestMetrics}
        {#if currentMetricData}
          <VizBody
            metricData={currentMetricData}
            currentDriftType={currentDriftType}
            currentName={currentName}
            currentTimeInterval={currentTimeInterval}
            currentConfig={currentConfig}
            currentProfile={currentProfile.profile}
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

    <!-- Row 3: 1 column  alerts -->
    <div class="bg-white p-2 border-2 border-black rounded-lg shadow min-h-[6rem] max-h-[30rem]">
      <AlertTable
        alerts={currentAlerts}
        updateAlert={updateAlert}
      />
    </div>




  </div>
 </div>
 