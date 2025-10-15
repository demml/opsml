<script lang="ts">
  import { DriftType } from "./types";
  import { type DriftConfigType, type UiProfile } from "./utils";
  import { Clock } from 'lucide-svelte';
  import { TimeInterval } from '$lib/components/card/monitoring/types';
  import { KeySquare } from 'lucide-svelte';
  import CustomConfigHeader from "./custom/CustomConfigHeader.svelte";
  import PsiConfigHeader from "./psi/PsiConfigHeader.svelte";
  import SpcConfigHeader from "./spc/SpcConfigHeader.svelte";
  import LLMConfigHeader from "./llm/LLMConfigHeader.svelte";
  import type { RegistryType } from "$lib/utils";
  import { Combobox } from "melt/builders";
  import ComboBoxDropDown from "$lib/components/utils/ComboBoxDropDown.svelte";


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
    uid,
    registry,
  } = $props<{
    availableDriftTypes: DriftType[];
    currentDriftType: DriftType;
    currentTimeInterval: TimeInterval;
    currentName: string;
    currentNames: string[];
    currentConfig: DriftConfigType;
    currentProfile: UiProfile;
    handleDriftTypeChange: (driftType: DriftType) => void;
    handleNameChange: (name: string) => void;
    handleTimeChange: (timeInterval: TimeInterval) => void;
    uid: string;
    registry: RegistryType;
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
  <div class="flex flex-col justify-center p-2 bg-white md:col-span-2 rounded-lg border-2 border-black shadow min-h-[4rem] px-4">
    <div class="flex flex-row flex-wrap gap-2 items-center justify-start mb-4">
      <div class="items-start mr-1 font-bold text-primary-800">Drift Type:</div>
        {#each availableDriftTypes as drift_type}
          {#if drift_type === currentDriftType}
            <button class="btn text-sm flex items-center gap-2 bg-slate-100 border-primary-800 border-2 rounded-lg">
              <div class="text-primary-800
              ">{drift_type}</div>
            </button>
          {:else}
            <button class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => handleDriftTypeChange(drift_type)}>
              <div class="text-black">{drift_type}</div>
            </button>
          {/if}
        {/each}
    </div>

    <div class="flex flex-row gap-3">

      <div class="flex flex-col gap-2 text-primary-800 self-center">
        <div class="font-bold">Time Interval:</div>
        <div class="flex flex-row gap-1">
          <div class="self-center" aria-label="Monitor Name">
            <Clock color="#5948a3" />
          </div>
          
          <ComboBoxDropDown
            boxId="interval-combobox-input"
            defaultValue={currentTimeInterval}
            boxOptions={timeIntervals}
          />
        </div>
      </div>
      
      
      <div class="flex flex-col gap-2 text-primary-800 self-center">
        <div class="font-bold">Name:</div>
        <div class="flex flex-row gap-1">
          <div class="self-center" aria-label="Monitor Name">
            <KeySquare color="#5948a3" />
          </div>
          
          <ComboBoxDropDown
            boxId="name-combobox-input"
            defaultValue={currentName ?? "Select Name"}
            boxOptions={currentNames}
          />
        </div>
      </div>
    </div>
  </div>

  <div class="bg-white p-4 rounded-lg shadow md:col-span-4 border-2 border-primary-800">
    {#if currentDriftType === DriftType.Custom}
      <CustomConfigHeader 
        config={currentConfig} 
        alertConfig={currentConfig.alert_config}
        profile={currentProfile}
        {uid}
        {registry}
      />

    {:else if currentDriftType === DriftType.LLM}
      <LLMConfigHeader
        config={currentConfig} 
        alertConfig={currentConfig.alert_config}
        profile={currentProfile}
        {uid}
        {registry}
      />

    {:else if currentDriftType === DriftType.Psi}
      <PsiConfigHeader 
        config={currentConfig} 
        alertConfig={currentConfig.alert_config}
        profile={currentProfile}
        {uid}
        {registry}
      />

    {:else if currentDriftType === DriftType.Spc}
      <SpcConfigHeader
        config={currentConfig} 
        alertConfig={currentConfig.alert_config}
        profile={currentProfile}
        {uid}
        {registry}
      />
    {/if}
  </div>
</div>