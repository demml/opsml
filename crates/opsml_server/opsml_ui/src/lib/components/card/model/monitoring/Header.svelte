<script lang="ts">
  import { DriftType } from "./types";
  import { type DriftConfigType, type DriftProfile, type DriftProfileResponse } from "./util";
  import { Clock } from 'lucide-svelte';
  import { TimeInterval } from '$lib/components/card/model/monitoring/types';
  import Dropdown from '$lib/components/utils/Dropdown.svelte';
  import { KeySquare } from 'lucide-svelte';
  import CustomConfigHeader from "./custom/CustomConfigHeader.svelte";
  import PsiConfigHeader from "./psi/PsiConfigHeader.svelte";
  import SpcConfigHeader from "./spc/SpcConfigHeader.svelte";


  // props
  let { 
    availableDriftTypes, 
    currentDriftType,
    currentTimeInterval = $bindable(),
    currentName = $bindable(),
    currentNames,
    currentConfig,
    currentProfile,
    handleDriftTypeChange,
    handleNameChange,
    handleTimeChange,
  } = $props<{
    availableDriftTypes: DriftType[];
    currentDriftType: DriftType;
    currentTimeInterval: TimeInterval;
    currentName: string;
    currentNames: string[];
    currentConfig: DriftConfigType;
    currentProfile: DriftProfile;
    handleDriftTypeChange: (driftType: DriftType) => void;
    handleNameChange: (name: string) => void;
    handleTimeChange: (timeInterval: TimeInterval) => void;
  }>();

  let timeIntervals = Object.values(TimeInterval);
  let previousName = $state(currentName);
  let previousTimeInterval = $state(currentTimeInterval);


  // Effect for handling a name change from the dropdown
  $effect(() => {
    if (currentName && currentName !== previousName) {
      previousName = currentName;
      handleNameChange(currentName);
    }
  });

  // Effect for handling a time interval change from the dropdown
  $effect(() => {
    if (currentTimeInterval && currentTimeInterval !== previousTimeInterval) {
      previousTimeInterval = currentTimeInterval;
      handleTimeChange(currentTimeInterval);
    }
  });



  

</script>

<div class="flex flex-row flex-wrap gap-4">

  <div class="flex flex-col justify-center p-4 bg-white p-4 md:col-span-2 rounded-lg border-2 border-black shadow min-h-[160px]">
    <div class="flex flex-row flex-wrap gap-2 items-center justify-center">
      <div class="items-center text-xl mr-2 font-bold text-primary-800">Drift Type:</div>
        {#each availableDriftTypes as drift_type}
          {#if drift_type === currentDriftType}
            <button class="btn flex items-center gap-2 bg-slate-100 border-primary-800 border-2 rounded-lg">
              <div class="text-primary-800
              ">{drift_type}</div>
            </button>
          {:else}
            <button class="btn flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => handleDriftTypeChange(drift_type)}>
              <div class="text-black">{drift_type}</div>
            </button>
          {/if}
        {/each}
    </div>

    <div class="flex flex-row flex-wrap gap-2 mt-4 items-center justify-center">
      <div class="flex gap-2 pr-2 border-primary-800">
        <div class="self-center" aria-label="Time Interval">
          <Clock color="#5948a3" />
        </div>

        <Dropdown 
          bind:selectedValue={currentTimeInterval}
          values={timeIntervals}
        />
      </div>

      <div class="flex items-center gap-2 pr-2">
        <div class="self-center" aria-label="Time Interval">
          <KeySquare color="#5948a3" />
        </div>

        <Dropdown 
          bind:selectedValue={currentName}
          bind:values={currentNames}
        />
      </div>
    </div>
  </div>

  <div class="bg-white p-4 rounded-lg shadow md:col-span-4 border-2 border-primary-800">
    {#if currentDriftType === DriftType.Custom}
      <CustomConfigHeader 
        config={currentConfig} 
        alertConfig={currentConfig.alert_config}
        profile={currentProfile}
      />

    {:else if currentDriftType === DriftType.Psi}
      <PsiConfigHeader 
        config={currentConfig} 
        alertConfig={currentConfig.alert_config}
        profile={currentProfile}
      />

    {:else if currentDriftType === DriftType.Spc}
      <SpcConfigHeader
        config={currentConfig} 
        alertConfig={currentConfig.alert_config}
        profile={currentProfile}
      />
    {/if}
  </div>
</div>



