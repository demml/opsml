<script lang="ts">
  import { KeySquare, ArrowUp } from "lucide-svelte";
  import Dropdown from "$lib/components/utils/Dropdown.svelte";
  import type { DataProfile, FeatureProfile } from "./types";
  import Pill from "$lib/components/utils/Pill.svelte";
  import NumericStats from "./NumericStats.svelte";
  import StringStats from "./StringStats.svelte";

  let { 
    features,
    profile
  } = $props<{
    features: string[];
    profile: DataProfile;
  }>();
  let selectedFeature = $state('choose feature');


  function scrollToFeature(feature: string) {
    if (feature === 'choose feature') return;
    
    const element = document.getElementById(`feature-${feature}`);
    if (element) {
      element.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  }

  $effect(() => {
    scrollToFeature(selectedFeature);
  });

  
</script>

<div class="relative">
  <!--Fixed div-->
  <div class="flex flex-row flex-wrap gap-2 items-center justify-center fixed left-1/2 transform -translate-x-1/2 z-10 bg-surface-50 py-2 w-full border-b-2 border-black">
    <div class="items-center text-lg mr-2 font-bold text-primary-800">Data Profile:</div>
    <div class="flex items-center gap-2 pr-2">
      <div class="self-center" aria-label="Time Interval">
        <KeySquare color="#5948a3" />
      </div>
  
      <Dropdown 
        bind:selectedValue={selectedFeature}
        bind:values={features}
        width='w-48'
        py="py-2"
      />
    </div>
  </div>


  <div class="grid grid-cols-1 gap-4 w-full pt-18 px-4">

    {#each features as feature}
      {@const featureProfile: FeatureProfile = profile.features[feature]}
        <div id="feature-{feature}" class="bg-white p-4 border-2 border-black rounded-lg shadow overflow-x-auto scroll-mt-16">
          <div class="flex flex-row flex-wrap gap-2 items-center">
            <Pill key="Name" value={featureProfile.id} textSize="text-sm"/>
            <Pill key="Created At" value={featureProfile.timestamp} textSize="text-sm"/>
            {#if !featureProfile.numeric_stats}
              <Pill key="Type" value="Categorical" textSize="text-sm"/>
            {:else}
              <Pill key="Type" value="Numeric" textSize="text-sm"/>
            {/if}
          </div>

          {#if featureProfile.numeric_stats}
            <NumericStats numericData={featureProfile.numeric_stats} />
          {:else if featureProfile.string_stats}
            <StringStats stringData={featureProfile.string_stats} />
          {/if}
        </div>
    {/each}

  </div>
</div>

