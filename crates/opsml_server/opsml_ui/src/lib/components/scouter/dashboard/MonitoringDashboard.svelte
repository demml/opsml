<script lang="ts">
  import { DriftType } from '$lib/components/scouter/types';
  import type { DriftProfileResponse } from '$lib/components/scouter/utils';
  import { getProfileDataWithConfig, isGenAIConfig, isCustomConfig, isPsiConfig, isSpcConfig } from '$lib/components/scouter/utils';
  import type { RegistryType } from '$lib/utils';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import MetricDashboard from '$lib/components/scouter/dashboard/metric/MetricDashboard.svelte';
  import type { TimeRange } from '$lib/components/trace/types';
  import { type GenAIEvalConfig } from '../genai/types';

  interface Props {
    profiles: DriftProfileResponse;
    driftTypes: DriftType[];
    initialDriftType: DriftType;
    uid: string;
    registryType: RegistryType;
    initialTimeRange: TimeRange;
    [key: string]: any;
  }

  let {
    profiles,
    driftTypes,
    initialDriftType,
    uid,
    registryType,
    initialTimeRange,
    ...rest
  }: Props = $props();

  let selectedDriftType = $state(initialDriftType);

  const currentData = $derived(() => {
    const data = getProfileDataWithConfig(profiles, selectedDriftType);
    console.log('Current drift type:', selectedDriftType);
    console.log('Current data:', data);
    return data;
  });
</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">

  {#if driftTypes.length > 1}
    <div class="flex flex-wrap gap-2 mb-4 p-4 bg-white rounded-lg border-2 border-black shadow">
      <span class="font-bold text-primary-800 mr-2">Drift Type:</span>
      {#each driftTypes as type}
        <button
          class="btn text-sm {type === selectedDriftType ? 'bg-slate-100 border-primary-800' : 'bg-primary-500 shadow shadow-hover'} border-2 border-black rounded-lg px-4 py-2"
          onclick={() => selectedDriftType = type}
        >
          {type}
        </button>
      {/each}
    </div>
  {/if}

  {#if selectedDriftType === DriftType.GenAI && isGenAIConfig(currentData().config)}
    <GenAIDashboard
      {uid}
      config={currentData().config as GenAIEvalConfig}
      profile={currentData().profile}
      {profiles}
      {initialTimeRange}
      initialRecords={rest.genAIEvalRecords}
      initialWorkflows={rest.genAIEvalWorkflows}
    />
  {:else if [DriftType.Spc, DriftType.Psi, DriftType.Custom].includes(selectedDriftType) && (isSpcConfig(currentData().config) || isPsiConfig(currentData().config) || isCustomConfig(currentData().config))}
    <MetricDashboard
      {uid}
      driftType={selectedDriftType}
      profile={currentData().profile}
      config={currentData().config}
      {profiles}
      {initialTimeRange}
      initialMetrics={rest.initialMetrics}
      initialAlerts={rest.driftAlerts}
      {registryType}
    />
  {/if}
</div>