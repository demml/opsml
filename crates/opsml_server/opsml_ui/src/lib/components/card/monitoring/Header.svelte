<script lang="ts">
  import { DriftType } from "./types";
  import { type DriftConfigType, type UiProfile } from "./utils";
  import { KeySquare } from 'lucide-svelte';
  import CustomConfigHeader from "./custom/CustomConfigHeader.svelte";
  import PsiConfigHeader from "./psi/PsiConfigHeader.svelte";
  import SpcConfigHeader from "./spc/SpcConfigHeader.svelte";
  import LLMConfigHeader from "./llm/LLMConfigHeader.svelte";
  import type { RegistryType } from "$lib/utils";
  import ComboBoxDropDown from "$lib/components/utils/ComboBoxDropDown.svelte";
  import TimeRangeFilter from "$lib/components/trace/TimeRangeFilter.svelte";
  import type { TimeRange } from "$lib/components/trace/types";

  let {
    availableDriftTypes,
    currentDriftType,
    selectedTimeRange = $bindable(),
    currentName = $bindable(),
    currentNames,
    currentConfig,
    currentProfile,
    handleDriftTypeChange,
    handleNameChange,
    handleTimeRangeChange,
    uid,
    registry,
  } = $props<{
    availableDriftTypes: DriftType[];
    currentDriftType: DriftType;
    selectedTimeRange: TimeRange;
    currentName: string;
    currentNames: string[];
    currentConfig: DriftConfigType;
    currentProfile: UiProfile;
    handleDriftTypeChange: (driftType: DriftType) => void;
    handleNameChange: (name: string) => void;
    handleTimeRangeChange: (range: TimeRange) => void;
    uid: string;
    registry: RegistryType;
  }>();

  let previousName = $state(currentName);

  $effect(() => {
    if (currentName && currentName !== previousName) {
      previousName = currentName;
      handleNameChange(currentName);
    }
  });
</script>

<div class="flex flex-wrap gap-4">
  <!-- Drift Type + Filters Row -->
  <div class="flex flex-col justify-center p-4 bg-white rounded-lg border-2 border-black shadow px-4 w-fit">
    <div class="flex flex-row flex-wrap gap-2 items-center justify-start mb-4">
      <span class="items-start mr-1 font-bold text-primary-800">Drift Type:</span>
      {#each availableDriftTypes as drift_type}
        {#if drift_type === currentDriftType}
          <button class="btn text-sm flex items-center gap-2 bg-slate-100 border-primary-800 border-2 rounded-lg">
            <div class="text-primary-800">{drift_type}</div>
          </button>
        {:else}
          <button class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => handleDriftTypeChange(drift_type)}>
            <div class="text-black">{drift_type}</div>
          </button>
        {/if}
      {/each}
    </div>

    <div class="flex flex-row gap-3">
      <!-- Time Range Selector -->
      <div class="flex flex-col gap-2 text-primary-800 self-center">
        <span class="font-bold">Time Range:</span>
        <TimeRangeFilter
          selectedRange={selectedTimeRange}
          onRangeChange={handleTimeRangeChange}
        />
      </div>

      <!-- Name Selector -->
      <div class="flex flex-col gap-2 text-primary-800 self-center">
        <span class="font-bold">Name:</span>
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

  <!-- Config Header -->
  <div class="bg-white p-4 rounded-lg shadow border-2 border-black w-fit">
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