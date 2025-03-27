<script lang="ts">
  import type { BinnedDriftMap, MetricData, SpcDriftFeature, BinnedPsiMetric, BinnedCustomMetric, BinnedCustomMetricStats  } from '$lib/components/monitoring/types';
  import { DriftType } from '$lib/components/monitoring/types';
  import type { DriftProfile, DriftProfileResponse } from '$lib/components/monitoring/util';
  import type { PageProps } from './$types';
  import { TimeInterval } from '$lib/components/monitoring/types';
  import VizBody from '$lib/components/monitoring/VizBody.svelte';
  import Header from '$lib/components/monitoring/Header.svelte';
  import TimeSeries from '$lib/components/viz/TimeSeries.svelte';
  import { onMount } from 'svelte';
 
 
  let { data }: PageProps = $props();

  let profiles: DriftProfileResponse = data.profiles;

  // Props
  let currentName: string = $state(data.currentName);
  let currentNames: string[] = $state(data.currentNames);
  let currentDriftType: DriftType = $state(data.currentDriftType);
  let currentProfile: DriftProfile = $state(data.currentProfile);
  let latestMetrics: BinnedDriftMap = $state(data.latestMetrics);
  let currentMetricData: MetricData = $state(data.currentMetricData);

  // Vars
  let drift_types: DriftType[] = data.keys;
  let currentTimeInterval: TimeInterval = $state(TimeInterval.SixHours);
  let isTimeDropdownOpen = $state(false);
  let isFeatureDropdownOpen = $state(false);


  // Effects
  
  // Refresh data
  $effect(() => {
    console.log('Metric name changed:', currentName);
    // get new data
    // if profile data has already been gotten for drifty_type, feature and interval, then do nothing
  });

  // Notify of profile change
  $effect(() => {
    console.log('Profile changed:', currentProfile);
    // get new data
    // if profile data has already been gotten for drifty_type, feature and interval, then do nothing
  });


 </script>
 
 <div class="mx-auto w-11/12 pb-10 flex justify-center">
  <div class="grid grid-cols-1 gap-4 w-full pt-4">

    <!--Create 3 row grid. First row contains 2 columns, 2nd row contains 1 column, 3rd row contains 1 col-->
    <div class="h-fit">
      <Header
            availableDriftTypes={drift_types}
            bind:currentDriftType={currentDriftType}
            profiles={profiles}
            bind:currentProfile={currentProfile}
            isTimeDropdownOpen={isTimeDropdownOpen}
            bind:currentTimeInterval={currentTimeInterval}
            isFeatureDropdownOpen={isFeatureDropdownOpen}
            bind:currentName={currentName}
            bind:currentNames={currentNames}
            currentConfig={data.currentConfig}
      /> 
    </div>

    <!-- Row 2: 1 column -->
    <div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
      
      {#if currentName && latestMetrics}
        {#if currentMetricData}
          <VizBody
            bind:metricData={currentMetricData}
            bind:currentDriftType={currentDriftType}
            bind:currentName={currentName}
            bind:currentTimeInterval={currentTimeInterval}
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
 