<script lang="ts">
  import { KeySquare } from "lucide-svelte";
  import type { DataProfile, FeatureProfile } from "./types";
  import Pill from "$lib/components/utils/Pill.svelte";
  import NumericStats from "./NumericStats.svelte";
  import StringStats from "./StringStats.svelte";
  import ComboBoxDropDown from "$lib/components/utils/ComboBoxDropDown.svelte";

  let { 
    features,
    profile
  } = $props<{
    features: string[];
    profile: DataProfile;
  }>();
  
  let dropdownInput = $state('');
  let selectedFeature = $state('');
  
  const filteredFeatures = $derived.by(() =>
    dropdownInput.trim()
      // @ts-ignore
      ? features.filter(f =>
          f.toLowerCase().includes(dropdownInput.trim().toLowerCase())
        )
      : features
  );

</script>

<div class="relative w-full">
  <!-- Fixed header instead of sticky to prevent movement -->
  <div class="fixed top-[120px] left-0 right-0 z-2 pt-4 bg-surface-50 border-b-2 border-black shadow-lg">
    <div class="max-w-full mx-auto">
      <div class="flex flex-row flex-wrap gap-2 items-center justify-center px-4 py-3">
        <div class="flex items-center gap-2 text-lg font-bold text-primary-800">
          <KeySquare color="#5948a3" size={20} aria-hidden="true" />
          <span>Data Profile:</span>
        </div>

        <ComboBoxDropDown
          boxId="feature-combobox-input"
          bind:defaultValue={selectedFeature}
          boxOptions={features}
          optionWidth="w-48"
          bind:inputValue={dropdownInput} 
        />
     
      </div>
    </div>
  </div>

  <!-- Content with proper top margin to account for fixed header -->
  <div class="mt-[80px] space-y-6 p-4">
    {#each filteredFeatures as feature}
      {@const featureProfile: FeatureProfile = profile.features[feature]}
      <div 
        id="feature-{feature}" 
        class="bg-white border-2 border-black rounded-lg shadow-md p-6 transition-shadow hover:shadow-lg w-full"
      >
        <!-- Feature metadata pills -->
        <div class="flex flex-row flex-wrap gap-2 items-center mb-4">
          <Pill key="Name" value={featureProfile.id} textSize="text-sm" />
          <Pill key="Created At" value={featureProfile.timestamp} textSize="text-sm" />
          <Pill 
            key="Type" 
            value={featureProfile.numeric_stats ? "Numeric" : "Categorical"} 
            textSize="text-sm" 
          />
        </div>

        <!-- Feature statistics -->
        {#if featureProfile.numeric_stats}
          <NumericStats numericData={featureProfile.numeric_stats} />
        {:else if featureProfile.string_stats}
          <StringStats stringData={featureProfile.string_stats} />
        {/if}
      </div>
    {/each}
  </div>
</div>