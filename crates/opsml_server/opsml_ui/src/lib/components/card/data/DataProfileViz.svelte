<script lang="ts">
  import { KeySquare, ArrowUp } from "lucide-svelte";
  import Dropdown from "$lib/components/utils/Dropdown.svelte";
  import type { DataProfile, FeatureProfile } from "./types";
  import Pill from "$lib/components/utils/Pill.svelte";
  import NumericStats from "./NumericStats.svelte";
  import StringStats from "./StringStats.svelte";
  import { onMount } from "svelte";

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


<div class="grid grid-cols-1 gap-4 w-full pt-4">
  <div class="flex flex-row flex-wrap gap-2 items-center justify-center">
    <div class="items-center text-xl mr-2 font-bold text-primary-800">Data Profile:</div>
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

  {#each features as feature}
    {@const featureProfile: FeatureProfile = profile.features[feature]}
      <div id="feature-{feature}" class="bg-white p-4 border-2 border-black rounded-lg shadow overflow-x-auto scroll-mt-4">
        <div class="flex flex-row flex-wrap gap-2 items-center">
          <Pill key="Name" value={featureProfile.id} />
          <Pill key="Created At" value={featureProfile.timestamp} />
          {#if !featureProfile.numeric_stats}
            <Pill key="Type" value="Categorical"/>
          {:else}
            <Pill key="Type" value="Numeric"/>
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


