<script lang="ts">
  import type { DriftType } from '$lib/components/monitoring/types';
  import type { DriftProfile, DriftProfileResponse } from '$lib/components/monitoring/util';
  import type { PageProps } from './$types';
  import { TimeInterval } from '$lib/components/monitoring/types';
  import Header from '$lib/components/monitoring/Header.svelte';
 
 
  let { data }: PageProps = $props();

  let profiles: DriftProfileResponse = data.profiles;

  // Props
  let currentName: string = $state(data.currentName);
  let currentNames: string[] = $state(data.currentNames);
  let currentDriftType: DriftType = $state(data.currentDriftType);
  let currentProfile: DriftProfile = $state(data.currentProfile);

  // Vars
  let drift_types: DriftType[] = data.keys;
  let currentInterval: TimeInterval = $state(TimeInterval.SixHours);
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
 
 <div class="mx-auto w-11/12 pb-10 flex justify-center min-h-screen">
  <div class="grid grid-cols-1 gap-4 w-full pt-4">

    <!--Create 3 row grid. First row contains 2 columns, 2nd row contains 1 column, 3rd row contains 1 col-->

    <div class="grid grid-cols-2 gap-4">
      
        <!-- First column content -->
         <Header
          availableDriftTypes={drift_types}
          bind:currentDriftType={currentDriftType}
          profiles={profiles}
          bind:currentProfile={currentProfile}
          isTimeDropdownOpen={isTimeDropdownOpen}
          bind:currentInterval={currentInterval}
          isFeatureDropdownOpen={isFeatureDropdownOpen}
          bind:currentName={currentName}
          bind:currentNames={currentNames}
         />
        
    </div>

    <!-- Row 2: 1 column -->
    <div class="bg-white p-4 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-2">Row 2</h2>
      <div class="h-full">Content for row 2</div>
    </div>

    <!-- Row 3: 1 column -->
    <div class="bg-white p-4 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-2">Row 3</h2>
      <div class="h-full">Content for row 3</div>
    </div>




  </div>
 </div>
 